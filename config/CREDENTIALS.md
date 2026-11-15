# What the cloud session needs from the owner (one-time)

1. Network (done via the "LAGO cloud edit" environment): www.googleapis.com, oauth2.googleapis.com, huggingface.co,
   cdn-lfs.huggingface.co, cdn-lfs-us-1.hf.co, cas-bridge.xethub.hf.co.
2. Google Drive API access from inside the container (the chat Drive connector cannot move multi-GB videos):
   - Option A (simplest, expires ~1 h): bearer token saved as a network secret for www.googleapis.com; use GDRIVE_AUTH=proxy.
   - Option B (autonomous): Google Cloud project -> enable Drive API -> OAuth client + refresh token
     (scope drive) -> GDRIVE_CLIENT_ID / GDRIVE_CLIENT_SECRET / GDRIVE_REFRESH_TOKEN.
   - Option C: service account; share ALARION + output folder with its e-mail; GDRIVE_SA_JSON.
   Secrets must not be committed; B/C values are stored as environment variables in plain text on the environment.
3. LUTs: drop the .cube files in a Drive folder (none were found by name search) and give its link.
