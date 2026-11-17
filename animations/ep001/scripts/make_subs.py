"""Align the definitive script (correct spelling) to Whisper word timings -> src/subtitles.json"""
import difflib, json, re, unicodedata

SCRIPT = open("script.txt", encoding="utf-8").read()
tr = json.load(open("work/tr.json"))
ww = [x for s in tr["segments"] for x in s["words"]]

def norm(t):
    t = unicodedata.normalize("NFD", t.lower())
    t = "".join(c for c in t if unicodedata.category(c) != "Mn")
    return re.sub(r"[^a-z0-9]", "", t)

# script tokens, keep punctuation attached for chunking
toks = SCRIPT.split()
sn = [norm(t) for t in toks]
wn = [norm(w["w"]) for w in ww]
# Whisper splits some names in two ("Jager"+"LeCoultre"): merge them into one token for matching
sm = difflib.SequenceMatcher(None, sn, wn, autojunk=False)
t_start = [None] * len(toks); t_end = [None] * len(toks)
for a, b, n in sm.get_matching_blocks():
    for k in range(n):
        t_start[a + k] = ww[b + k]["start"]; t_end[a + k] = ww[b + k]["end"]
# fill gaps by interpolation between known neighbours
known = [i for i, v in enumerate(t_start) if v is not None]
for i in range(len(toks)):
    if t_start[i] is None:
        p = max([k for k in known if k < i], default=None); q = min([k for k in known if k > i], default=None)
        t0 = t_end[p] if p is not None else 0.0
        t1 = t_start[q] if q is not None else tr["duration"]
        gap = [j for j in range(len(toks)) if t_start[j] is None and (p is None or j > p) and (q is None or j < q)]
        idx = gap.index(i)
        t_start[i] = t0 + (t1 - t0) * idx / len(gap); t_end[i] = t0 + (t1 - t0) * (idx + 1) / len(gap)

# chunking: break at sentence/clause punctuation, then max 4 words, never leave a 1-word orphan
chunks, cur = [], []
for i, t in enumerate(toks):
    cur.append(i)
    if re.search(r"[.,;:?!]$", t) or len(cur) >= 4:
        chunks.append(cur); cur = []
if cur: chunks.append(cur)
merged = []
for c in chunks:
    prev_end = toks[merged[-1][-1]] if merged else ""
    if merged and len(c) == 1 and len(merged[-1]) < 5 and not re.search(r"[.?!]$", prev_end): merged[-1] += c
    else: merged.append(c)
HI = {"robertpattinson", "jamesbond", "omega", "jaegerlecoultre", "rolex", "1995", "007", "1962", "reverso", "polaris", "seamaster", "submariner"}
out = []
for k, c in enumerate(merged):
    words = [toks[i].strip("¿?¡!,.;:") if False else toks[i] for i in c]
    s = t_start[c[0]]; e = t_end[c[-1]]
    nxt = t_start[merged[k + 1][0]] if k + 1 < len(merged) else e + 0.6
    e = min(max(e + 0.12, s + 0.5), nxt - 0.02) if nxt - e < 0.5 else e + 0.35
    out.append({"start": round(s, 2), "end": round(e, 2), "words": [{"t": toks[i], "hi": norm(toks[i]) in HI} for i in c]})
# highlight two-word names: "Robert Pattinson", "James Bond", "Jaeger-LeCoultre"
for ch in out:
    w = ch["words"]
    for j in range(len(w) - 1):
        a, b = norm(w[j]["t"]), norm(w[j + 1]["t"])
        if (a, b) in {("robert", "pattinson"), ("james", "bond"), ("sean", "connery")}:
            w[j]["hi"] = w[j + 1]["hi"] = True
json.dump(out, open("src/subtitles.json", "w"), ensure_ascii=False, indent=1)
print(len(out), "chunks"); [print(f"{c['start']:5.2f}-{c['end']:5.2f}", " ".join(w['t'] for w in c['words'])) for c in out]
