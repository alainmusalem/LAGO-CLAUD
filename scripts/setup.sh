#!/usr/bin/env bash
# Idempotent setup for a fresh cloud container. Run from anywhere.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
command -v ffmpeg >/dev/null || { apt-get update -y && apt-get install -y ffmpeg; }
python3 -m pip install -q --break-system-packages -r requirements.txt 2>/dev/null || python3 -m pip install -q -r requirements.txt
(cd remotion && npm install --no-audit --no-fund --silent)
echo "setup ok: $(ffmpeg -version | head -1)"
python3 -c "import faster_whisper; print('faster-whisper', faster_whisper.__version__)"
