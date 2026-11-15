// node broker/test.mjs — end-to-end test of the Worker with a mocked Google (no network, no credentials).
import worker from "./worker.js";
const calls = [];
globalThis.fetch = async (url, init = {}) => {
  url = String(url);
  if (url.includes("oauth2.googleapis.com")) return new Response(JSON.stringify({ access_token: "AT", expires_in: 3600 }));
  calls.push({ url, method: init.method, auth: init.headers?.get("Authorization") });
  return new Response("{}", { status: 200, headers: url.includes("uploadType=resumable") && init.method === "POST" ? { Location: "https://www.googleapis.com/upload/drive/v3/files?uploadType=resumable&upload_id=XYZ" } : {} });
};
const env = { BROKER_KEY: "k", G_CLIENT_ID: "c", G_CLIENT_SECRET: "s", G_REFRESH_TOKEN: "r" };
const B = "https://b.example.workers.dev", id = "1AbCdEfGhIjKlMnOp";
const call = (method, path, body, key = "k") => worker.fetch(new Request(B + path, { method, headers: { Authorization: "Bearer " + key, ...(body ? { "Content-Type": "application/json" } : {}) }, body: body ? JSON.stringify(body) : undefined }), env);
const cases = [
  // [expected status, method, path, body]
  [200, "GET", "/drive/v3/files?q=name%20contains%20%27ALARION%27"],
  [200, "GET", `/drive/v3/files/${id}?alt=media`],
  [200, "POST", "/drive/v3/files", { name: "NUEVA", mimeType: "application/vnd.google-apps.folder", parents: [id] }],
  [200, "PATCH", `/drive/v3/files/${id}`, { name: "renombrado" }],
  [200, "PATCH", `/drive/v3/files/${id}?addParents=${id}A&removeParents=${id}B`, {}],
  [200, "POST", `/drive/v3/files/${id}/copy`, { name: "copia" }],
  [200, "POST", "/upload/drive/v3/files?uploadType=resumable", { name: "final.mp4", parents: [id] }],
  [200, "PUT", "/upload/drive/v3/files?uploadType=resumable&upload_id=XYZ"],
  [403, "DELETE", `/drive/v3/files/${id}`],
  [403, "DELETE", "/drive/v3/files/trash"],
  [403, "PATCH", `/drive/v3/files/${id}`, { trashed: true }],
  [403, "PATCH", `/drive/v3/files/${id}`, { explicitlyTrashed: true }],
  [403, "PATCH", `/drive/v3/files/${id}?uploadType=media`, null],
  [403, "PATCH", `/upload/drive/v3/files/${id}?uploadType=resumable`, { name: "x" }],
  [403, "PUT", `/upload/drive/v3/files/${id}?uploadType=resumable&upload_id=XYZ`],
  [403, "PUT", "/upload/drive/v3/files?uploadType=media"],
  [403, "PATCH", `/drive/v3/files/${id}?removeParents=${id}B`, {}],
  [403, "POST", `/drive/v3/files/${id}/permissions`, { role: "reader", type: "anyone" }],
  [403, "PATCH", `/drive/v3/files/${id}/permissions/${id}`, { role: "owner" }],
  [403, "GET", `/drive/v3/files/${id}/permissions`],
  [403, "POST", "/drive/v3/files", { name: "x", trashed: true }],
  [403, "POST", `/drive/v3/files/${id}/watch`, {}],
  [200, "GET", `/drive/v3/files/${id}/../${id}`],  // URL parser normalises to a plain allowed read
  [403, "POST", `/drive/v3/files/${id}/%2e%2e/trash`],
  [401, "GET", "/drive/v3/files", null, "wrong"],
];
let bad = 0;
for (const [exp, m, p, b, key] of cases) {
  const before = calls.length;
  const r = await call(m, p, b, key);
  const forwarded = calls.length > before;
  const pass = r.status === exp && (exp === 200) === forwarded;
  if (!pass) bad++;
  console.log(pass ? "ok  " : "FAIL", exp, r.status, m, p.slice(0, 70), forwarded ? "(forwarded)" : "(not forwarded)");
}
const loc = (await call("POST", "/upload/drive/v3/files?uploadType=resumable", { name: "a" })).headers.get("Location");
console.log(loc.startsWith(B) ? "ok   Location rewritten to broker" : "FAIL Location " + loc); if (!loc.startsWith(B)) bad++;
console.log(calls.every((c) => c.auth === "Bearer AT") ? "ok   Google only ever sees the broker-held token" : "FAIL"); 
process.exit(bad ? 1 : 0);
