"""Google Drive v3 client (REST). Large-file safe: streamed download with resume, resumable upload.

Auth, first match wins (see config/README for how to provide each):
  GDRIVE_AUTH=proxy            -> no header added; the sandbox network proxy injects the credential
  GDRIVE_ACCESS_TOKEN          -> short-lived bearer token
  GDRIVE_REFRESH_TOKEN + GDRIVE_CLIENT_ID + GDRIVE_CLIENT_SECRET -> OAuth refresh flow (recommended)
  GDRIVE_SA_JSON (path or JSON) -> service account (folders must be shared with its e-mail)
"""
import json, os, time
import requests

# Broker mode (recommended): the agent holds only GDRIVE_BROKER_KEY; the OAuth credentials live in the Worker (see broker/).
_BASE = os.environ.get("GDRIVE_BROKER_URL", "https://www.googleapis.com").rstrip("/")
API = _BASE + "/drive/v3"
UPLOAD = _BASE + "/upload/drive/v3/files"
SCOPES = ["https://www.googleapis.com/auth/drive"]
FOLDER = "application/vnd.google-apps.folder"
_cache = {"tok": None, "exp": 0}


def _headers():
    if os.environ.get("GDRIVE_BROKER_KEY"):
        return {"Authorization": "Bearer " + os.environ["GDRIVE_BROKER_KEY"]}
    if os.environ.get("GDRIVE_AUTH") == "proxy":
        return {}
    if os.environ.get("GDRIVE_ACCESS_TOKEN"):
        return {"Authorization": "Bearer " + os.environ["GDRIVE_ACCESS_TOKEN"]}
    if time.time() < _cache["exp"] - 60 and _cache["tok"]:
        return {"Authorization": "Bearer " + _cache["tok"]}
    from google.auth.transport.requests import Request
    if os.environ.get("GDRIVE_REFRESH_TOKEN"):
        from google.oauth2.credentials import Credentials
        cred = Credentials(None, refresh_token=os.environ["GDRIVE_REFRESH_TOKEN"],
                           client_id=os.environ["GDRIVE_CLIENT_ID"], client_secret=os.environ["GDRIVE_CLIENT_SECRET"],
                           token_uri="https://oauth2.googleapis.com/token", scopes=SCOPES)
    elif os.environ.get("GDRIVE_SA_JSON"):
        from google.oauth2 import service_account
        raw = os.environ["GDRIVE_SA_JSON"]
        info = json.loads(raw) if raw.lstrip().startswith("{") else json.load(open(raw))
        cred = service_account.Credentials.from_service_account_info(info, scopes=SCOPES)
    else:
        raise SystemExit("No Drive credentials: set GDRIVE_AUTH=proxy, GDRIVE_ACCESS_TOKEN, GDRIVE_REFRESH_TOKEN(+CLIENT_ID/SECRET) or GDRIVE_SA_JSON")
    cred.refresh(Request())
    _cache.update(tok=cred.token, exp=cred.expiry.timestamp() if cred.expiry else time.time() + 3000)
    return {"Authorization": "Bearer " + cred.token}


def _req(method, url, **kw):
    for attempt in range(5):
        r = requests.request(method, url, headers={**_headers(), **kw.pop("headers", {})}, timeout=120, **kw)
        if r.status_code in (429, 500, 502, 503, 504):
            time.sleep(2 ** attempt); continue
        if r.status_code >= 400:
            raise RuntimeError(f"Drive {method} {url} -> {r.status_code}: {r.text[:300]}")
        return r
    raise RuntimeError("Drive request failed after retries")


FIELDS = "id,name,mimeType,size,createdTime,modifiedTime,parents,videoMediaMetadata,md5Checksum"


def search(q, page_size=100):
    out, tok = [], None
    while True:
        p = {"q": q + " and trashed=false", "fields": f"nextPageToken,files({FIELDS})", "pageSize": page_size,
             "supportsAllDrives": "true", "includeItemsFromAllDrives": "true", "orderBy": "modifiedTime desc"}
        if tok: p["pageToken"] = tok
        j = _req("GET", API + "/files", params=p).json()
        out += j.get("files", [])
        tok = j.get("nextPageToken")
        if not tok: return out


def children(folder_id):
    return search(f"'{folder_id}' in parents")


def walk(folder_id, path=""):
    """Yield (path, file) recursively."""
    for f in children(folder_id):
        p = f"{path}/{f['name']}"
        if f["mimeType"] == FOLDER:
            yield from walk(f["id"], p)
        else:
            yield p, f


def meta(file_id):
    return _req("GET", f"{API}/files/{file_id}", params={"fields": FIELDS, "supportsAllDrives": "true"}).json()


def download(file_id, dest, chunk=8 << 20):
    """Stream to dest; resumes a partial file. Never touches anything on Drive."""
    size = int(meta(file_id)["size"])
    have = os.path.getsize(dest) if os.path.exists(dest) else 0
    if have > size: os.remove(dest); have = 0
    while have < size:
        r = _req("GET", f"{API}/files/{file_id}", params={"alt": "media", "supportsAllDrives": "true"},
                 headers={"Range": f"bytes={have}-"}, stream=True)
        with open(dest, "ab") as f:
            for b in r.iter_content(chunk):
                f.write(b); have += len(b)
    return dest


def download_range(file_id, dest, nbytes):
    """First nbytes only (cheap probing of container header / thumbnails)."""
    r = _req("GET", f"{API}/files/{file_id}", params={"alt": "media", "supportsAllDrives": "true"},
             headers={"Range": f"bytes=0-{nbytes-1}"})
    open(dest, "wb").write(r.content)
    return dest


def mkdir(name, parent):
    ex = search(f"'{parent}' in parents and name='{name}' and mimeType='{FOLDER}'")
    if ex: return ex[0]["id"]
    return _req("POST", API + "/files", params={"supportsAllDrives": "true"},
                json={"name": name, "mimeType": FOLDER, "parents": [parent]}).json()["id"]


def upload(path, parent, name=None, mime="application/octet-stream", chunk=32 << 20):
    """Resumable upload; always creates a NEW file (never overwrites an existing Drive file)."""
    name = name or os.path.basename(path)
    total = os.path.getsize(path)
    init = _req("POST", UPLOAD, params={"uploadType": "resumable", "supportsAllDrives": "true"},
                headers={"X-Upload-Content-Type": mime, "X-Upload-Content-Length": str(total)},
                json={"name": name, "parents": [parent]})
    url, pos = init.headers["Location"], 0
    with open(path, "rb") as f:
        while pos < total:
            buf = f.read(chunk)
            end = pos + len(buf) - 1
            r = requests.put(url, data=buf, headers={**_headers(), "Content-Range": f"bytes {pos}-{end}/{total}"}, timeout=300)
            if r.status_code in (200, 201):
                return r.json()
            if r.status_code != 308:
                raise RuntimeError(f"upload failed {r.status_code}: {r.text[:300]}")
            pos = end + 1
    raise RuntimeError("upload ended without completion")


def rename(file_id, new_name):
    return _req("PATCH", f"{API}/files/{file_id}", params={"supportsAllDrives": "true"}, json={"name": new_name}).json()


def move(file_id, new_parent):
    """Re-parent (never removes a file from Drive; the broker refuses removeParents without addParents)."""
    old = ",".join(meta(file_id).get("parents", []))
    return _req("PATCH", f"{API}/files/{file_id}", params={"supportsAllDrives": "true", "addParents": new_parent, "removeParents": old}, json={}).json()
