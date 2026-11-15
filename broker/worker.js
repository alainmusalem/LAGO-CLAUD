// LAGO Drive broker — Cloudflare Worker. Holds the Google OAuth credentials; the agent only ever holds BROKER_KEY.
// DENY BY DEFAULT: anything not matched by an explicit rule below is rejected with 403.
// Secrets (Worker > Settings > Variables, type "Secret"): BROKER_KEY, G_CLIENT_ID, G_CLIENT_SECRET, G_REFRESH_TOKEN
const G = "https://www.googleapis.com";
const ID = "[A-Za-z0-9_-]{10,}";
const SAFE_QUERY = new Set(["fields", "supportsAllDrives", "includeItemsFromAllDrives", "supportsTeamDrives", "includeTeamDriveItems",
  "q", "pageSize", "pageToken", "orderBy", "corpora", "driveId", "spaces", "alt", "acknowledgeAbuse", "mimeType", "count", "space", "includeLabels", "includePermissionsForView"]);
const META_KEYS = new Set(["name", "description", "starred"]);                       // PATCH body: rename/describe only
const CREATE_KEYS = new Set(["name", "parents", "mimeType", "description", "id", "starred", "appProperties", "properties", "modifiedTime", "createdTime"]);
const deny = (why) => ({ ok: false, why });

// Pure policy function: returns {ok:true} or {ok:false, why}. `body` is a parsed JSON object or null.
function authorize(method, url, body) {
  const u = new URL(url);
  const p = u.pathname.replace(/\/+$/, "");
  if (/%2e|%2f|\.\./i.test(u.pathname)) return deny("suspicious path");
  const q = u.searchParams;
  const keys = [...q.keys()];
  const only = (allowed) => keys.every((k) => allowed.has(k));
  const m = (re) => p.match(new RegExp("^" + re + "$"));

  // ---- reads: search, list, metadata, download (alt=media), export, revisions metadata, about ----
  if (method === "GET") {
    if (m("/drive/v3/files") || m(`/drive/v3/files/${ID}`) || m(`/drive/v3/files/${ID}/export`) ||
        m("/drive/v3/about") || m("/drive/v3/files/generateIds") || m(`/drive/v3/files/${ID}/revisions`)) {
      return only(new Set([...SAFE_QUERY])) ? { ok: true } : deny("query parameter not allowed");
    }
    return deny("GET route not allowed");
  }
  // ---- create new file/folder (metadata only) ----
  if (method === "POST" && m("/drive/v3/files")) {
    if (body && (body.trashed || body.explicitlyTrashed)) return deny("create as trashed");
    if (body && !Object.keys(body).every((k) => CREATE_KEYS.has(k))) return deny("body field not allowed on create");
    return only(SAFE_QUERY) ? { ok: true } : deny("query parameter not allowed");
  }
  // ---- copy (always creates a new file) ----
  if (method === "POST" && m(`/drive/v3/files/${ID}/copy`)) {
    if (body && (body.trashed || body.explicitlyTrashed)) return deny("copy as trashed");
    return only(SAFE_QUERY) ? { ok: true } : deny("query parameter not allowed");
  }
  // ---- rename / describe / move. Never trash, never content, never permissions ----
  if (method === "PATCH" && m(`/drive/v3/files/${ID}`)) {
    if (q.has("uploadType")) return deny("content update (overwrite) blocked");
    if (body && !Object.keys(body).every((k) => META_KEYS.has(k))) return deny("PATCH body may only change name/description/starred");
    if (q.has("removeParents") && !q.has("addParents")) return deny("removeParents without addParents would orphan the file");
    return only(new Set([...SAFE_QUERY, "addParents", "removeParents"])) ? { ok: true } : deny("query parameter not allowed");
  }
  // ---- upload NEW files only (POST /upload/drive/v3/files). Overwrite = PATCH/PUT on /files/{id}: blocked ----
  if (method === "POST" && m("/upload/drive/v3/files")) {
    const t = q.get("uploadType");
    if (!["resumable", "multipart", "media"].includes(t)) return deny("uploadType");
    if (body && (body.trashed || body.explicitlyTrashed)) return deny("upload as trashed");
    return only(new Set([...SAFE_QUERY, "uploadType", "uploadType"])) ? { ok: true } : deny("query parameter not allowed");
  }
  // ---- continue a resumable session created above (the upload_id binds it to a NEW file) ----
  if (method === "PUT" && m("/upload/drive/v3/files") && q.get("uploadType") === "resumable" && q.get("upload_id")) {
    return only(new Set(["uploadType", "upload_id", "supportsAllDrives", "fields"])) ? { ok: true } : deny("query parameter not allowed");
  }
  return deny(`${method} ${p} is not on the allow-list`);   // DELETE, emptyTrash, permissions, watch, labels, PATCH/PUT on /upload/.../{id}, ...
}

let cached = { tok: null, exp: 0 };
async function accessToken(env) {
  if (cached.tok && Date.now() < cached.exp - 60000) return cached.tok;
  const r = await fetch("https://oauth2.googleapis.com/token", {
    method: "POST", headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body: new URLSearchParams({ client_id: env.G_CLIENT_ID, client_secret: env.G_CLIENT_SECRET, refresh_token: env.G_REFRESH_TOKEN, grant_type: "refresh_token" }),
  });
  const j = await r.json();
  if (!j.access_token) throw new Error("token refresh failed: " + JSON.stringify(j).slice(0, 200));
  cached = { tok: j.access_token, exp: Date.now() + j.expires_in * 1000 };
  return cached.tok;
}

const timingSafeEq = (a, b) => { if (a.length !== b.length) return false; let d = 0; for (let i = 0; i < a.length; i++) d |= a.charCodeAt(i) ^ b.charCodeAt(i); return d === 0; };

export default {
  async fetch(req, env) {
    const auth = req.headers.get("Authorization") || "";
    if (!env.BROKER_KEY || !timingSafeEq(auth, "Bearer " + env.BROKER_KEY)) return new Response("unauthorized", { status: 401 });
    let body = null;
    const ct = req.headers.get("Content-Type") || "";
    // Only small JSON bodies are inspected; file bytes stream straight through.
    if (["POST", "PATCH"].includes(req.method) && ct.includes("application/json")) {
      const txt = await req.clone().text();
      try { body = txt ? JSON.parse(txt) : null; } catch { return new Response("bad json", { status: 400 }); }
    }
    const verdict = authorize(req.method, req.url, body);
    console.log(JSON.stringify({ t: new Date().toISOString(), m: req.method, p: new URL(req.url).pathname, ok: verdict.ok, why: verdict.why }));
    if (!verdict.ok) return new Response(JSON.stringify({ error: "blocked by broker policy", reason: verdict.why }), { status: 403, headers: { "Content-Type": "application/json" } });

    const src = new URL(req.url);
    const target = G + src.pathname + src.search;
    const h = new Headers();
    for (const k of ["content-type", "content-length", "content-range", "range", "x-upload-content-type", "x-upload-content-length"]) {
      if (req.headers.get(k)) h.set(k, req.headers.get(k));
    }
    h.set("Authorization", "Bearer " + await accessToken(env));
    const up = await fetch(target, { method: req.method, headers: h, body: ["GET", "HEAD"].includes(req.method) ? undefined : req.body });
    const out = new Headers(up.headers);
    const loc = out.get("Location");                       // keep resumable sessions flowing through the broker
    if (loc) out.set("Location", loc.replace(G, new URL(req.url).origin));
    return new Response(up.body, { status: up.status, headers: out });
  },
};
