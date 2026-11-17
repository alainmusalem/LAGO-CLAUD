# LAGO-CLAUD — cloud editing toolkit

Autonomous, cloud-only pipeline: Drive (media in/out) → Whisper → cut-only EDL → FFmpeg (9:16, LUT, loudness) → Drive.
GitHub holds code/config only; media never enters git (`.gitignore`).

    scripts/setup.sh                      # ffmpeg, faster-whisper, google-auth, remotion deps
    python -m lago drive-find "name contains 'C01'"
    python -m lago drive-pull FILE_ID work/src.mp4
    python -m lago probe work/src.mp4     # colour profile decision (rec709 / log_suspected / hlg / pq)
    python -m lago transcribe work/src.mp4 work/tr.json small
    python -m lago edit work/tr.json work/src.mp4 work/edl.json   # proposal + CMX3600 .edl (opens in Resolve)
    # review/adjust work/edl.json, then:
    python -m lago render work/edl.json work/src.mp4 out/final.mp4 [--lut luts/x.cube --lut-in rec709]
    python -m lago drive-push out/final.mp4 FOLDER_ID

Safety: Drive access never overwrites (uploads create new files); the LUT step refuses mismatched input profiles.
Editable project = `edl.json` (+ `.edl` for DaVinci Resolve, + `remotion/` composition driven by the same JSON).
Auth/credentials: see `config/CREDENTIALS.md`.
