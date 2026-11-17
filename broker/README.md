# Drive broker (Cloudflare Worker)

Single file `worker.js`, deny-by-default. Deploy it yourself (dashboard editor); the agent never gets Cloudflare access,
so it cannot loosen the policy. `node broker/test.mjs` runs the allow/deny matrix against a mocked Google.

Allowed: search/list/read/download/export, create folder/file, copy, rename/describe/star, move (addParents+removeParents together),
upload NEW files (resumable/multipart/media). Blocked: DELETE, trash/emptyTrash, trashed=true, content overwrite
(PATCH/PUT on an existing file id or uploadType on files.update), permissions, watch, labels, and any route not listed.
