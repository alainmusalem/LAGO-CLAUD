"""Whisper (faster-whisper) transcription with word timestamps. Saves JSON next to the work files."""
import json, os, subprocess, sys


def extract_audio(video, wav):
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", video, "-vn", "-ac", "1", "-ar", "16000", wav], check=True)
    return wav


def transcribe(video, out_json, model="small", language="es", device="cpu", compute="int8"):
    from faster_whisper import WhisperModel
    wav = os.path.splitext(out_json)[0] + ".wav"
    extract_audio(video, wav)
    m = WhisperModel(model, device=device, compute_type=compute, download_root=os.environ.get("WHISPER_CACHE", os.path.expanduser("~/.cache/lago-whisper")))
    # vad_filter=False on purpose: we want silences/false starts reported, not hidden. no prior-text conditioning avoids hallucinated loops.
    segs, info = m.transcribe(wav, language=language, word_timestamps=True, vad_filter=False, condition_on_previous_text=False, beam_size=5)
    data = {"language": info.language, "duration": info.duration, "model": model, "segments": []}
    for s in segs:
        data["segments"].append({"start": s.start, "end": s.end, "text": s.text.strip(), "avg_logprob": s.avg_logprob,
                                 "words": [{"w": w.word, "start": w.start, "end": w.end, "p": w.probability} for w in (s.words or [])]})
    json.dump(data, open(out_json, "w"), ensure_ascii=False, indent=1)
    return data


if __name__ == "__main__":
    transcribe(sys.argv[1], sys.argv[2], *(sys.argv[3:4] or ["small"]))
