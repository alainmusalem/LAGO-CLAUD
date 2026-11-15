"""Transcript -> cut-only edit decision list (EDL).

Heuristics produce a *proposal*; the operator/agent reviews the transcript and may edit the JSON before render.
Rules: cuts land inside silences (never inside a word), natural pauses <= max_pause are kept, longer gaps are shortened,
repeated/aborted takes keep the LAST complete one, lead-in/out silence is trimmed with small handles.
"""
import difflib, json, re

PAD = 0.12          # handle kept before first / after last word of a kept span (s)
MAX_PAUSE = 0.9     # pauses up to this are natural and kept untouched
KEEP_PAUSE = 0.55   # longer pauses are shortened to this
FILLERS = {"eh", "em", "mm", "mmm", "ehh", "este", "pues"}


def _norm(t):
    return re.sub(r"[^\w\s]", "", t.lower()).strip()


def flatten(tr):
    return [dict(w, seg=i) for i, s in enumerate(tr["segments"]) for w in s["words"]]


def sentences(tr, gap=0.6):
    """Group words into utterances at punctuation or gaps > `gap`."""
    out, cur = [], []
    for w in flatten(tr):
        if cur and (w["start"] - cur[-1]["end"] > gap):
            out.append(cur); cur = []
        cur.append(w)
        if re.search(r"[.!?…]$", w["w"].strip()):
            out.append(cur); cur = []
    if cur: out.append(cur)
    return [{"start": u[0]["start"], "end": u[-1]["end"], "text": "".join(x["w"] for x in u).strip(), "words": u} for u in out]


def analyse(tr, sim=0.72):
    """Flag repeated takes (similar to the next utterance) and low-confidence/aborted fragments."""
    us = sentences(tr)
    for i, u in enumerate(us):
        u["drop"], u["why"] = False, None
        nxt = us[i + 1] if i + 1 < len(us) else None
        toks = len(_norm(u["text"]).split())
        if nxt:
            r = difflib.SequenceMatcher(None, _norm(u["text"]), _norm(nxt["text"])).ratio()
            if r >= sim and toks >= 2:
                u["drop"], u["why"] = True, f"retake: next utterance is {r:.0%} similar (keep the last)"
            elif toks <= 3 and nxt["start"] - u["end"] < 1.5 and _norm(nxt["text"]).startswith(_norm(u["text"])[:max(3, len(_norm(u['text'])) - 2)]):
                u["drop"], u["why"] = True, "false start: restarted immediately"
        if not u["drop"] and toks and all(t in FILLERS for t in _norm(u["text"]).split()):
            u["drop"], u["why"] = True, "filler only"
    return us


def build_edl(tr, src, fps, duration, sim=0.72):
    us = analyse(tr, sim)
    keep = [u for u in us if not u["drop"]]
    segs = []
    for u in keep:
        s, e = max(0, u["start"] - PAD), min(duration, u["end"] + PAD)
        if segs and s - segs[-1]["end"] <= MAX_PAUSE and not segs[-1].get("_cut_after"):
            segs[-1]["end"] = e; segs[-1]["text"] += " " + u["text"]
        else:
            segs.append({"start": s, "end": e, "text": u["text"]})
        if segs and u is not keep[-1]:
            nxt = keep[keep.index(u) + 1]
            if nxt["start"] - u["end"] > MAX_PAUSE:
                segs[-1]["_cut_after"] = True
    # Shorten long pauses by splitting the kept range into separate segments (the pause is trimmed between them).
    for s in segs: s.pop("_cut_after", None)
    for i in range(len(segs) - 1):      # long pauses collapse to KEEP_PAUSE, split evenly across the cut
        extra = (KEEP_PAUSE - 2 * PAD) / 2
        if extra > 0 and segs[i + 1]["start"] - segs[i]["end"] > KEEP_PAUSE:
            segs[i]["end"] += extra; segs[i + 1]["start"] -= extra
    for i in range(len(segs) - 1):      # avoid overlaps from handles
        if segs[i]["end"] > segs[i + 1]["start"]:
            mid = (segs[i]["end"] + segs[i + 1]["start"]) / 2
            segs[i]["end"] = segs[i + 1]["start"] = mid
    return {"source": src, "fps": fps, "duration": duration, "segments": segs,
            "dropped": [{"start": u["start"], "end": u["end"], "text": u["text"], "why": u["why"]} for u in us if u["drop"]]}


def snap_to_silence(edl, words):
    """Move every cut point into the widest nearby gap between words so no word is clipped."""
    gaps = [(a["end"], b["start"]) for a, b in zip(words, words[1:]) if b["start"] - a["end"] > 0.04]
    def snap(t, edge):
        for ws in words:                      # t falls inside a word -> push out of it
            if ws["start"] < t < ws["end"]:
                t = ws["start"] - 0.03 if edge == "start" else ws["end"] + 0.03
        return max(0, t)
    for s in edl["segments"]:
        s["start"], s["end"] = snap(s["start"], "start"), snap(s["end"], "end")
    return edl


def edl_cmx3600(edl, title="LAGO EDIT", reel="SRC"):
    """CMX3600 EDL importable in DaVinci Resolve / Premiere (File > Import > Timeline)."""
    fps = round(edl["fps"])
    tc = lambda t: "%02d:%02d:%02d:%02d" % (int(t // 3600), int(t % 3600 // 60), int(t % 60), int(round((t % 1) * fps)) % fps)
    lines, rec = [f"TITLE: {title}", "FCM: NON-DROP FRAME", ""], 0.0
    for i, s in enumerate(edl["segments"], 1):
        d = s["end"] - s["start"]
        lines.append(f"{i:03d}  {reel:<8} V     C        {tc(s['start'])} {tc(s['end'])} {tc(rec)} {tc(rec + d)}")
        lines.append(f"{i:03d}  {reel:<8} A     C        {tc(s['start'])} {tc(s['end'])} {tc(rec)} {tc(rec + d)}")
        lines.append(f"* FROM CLIP NAME: {edl['source']}\n")
        rec += d
    return "\n".join(lines)


def load(p): return json.load(open(p))
def save(o, p): json.dump(o, open(p, "w"), ensure_ascii=False, indent=1)
