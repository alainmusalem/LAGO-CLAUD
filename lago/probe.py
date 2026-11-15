"""ffprobe + signal statistics -> colour profile decision BEFORE any LUT is chosen."""
import json, re, subprocess


def _run(cmd):
    return subprocess.run(cmd, capture_output=True, text=True, check=True).stdout


def probe(path):
    j = json.loads(_run(["ffprobe", "-v", "error", "-print_format", "json", "-show_format", "-show_streams", path]))
    v = next(s for s in j["streams"] if s["codec_type"] == "video")
    a = next((s for s in j["streams"] if s["codec_type"] == "audio"), None)
    num, den = map(int, v["r_frame_rate"].split("/"))
    rot = 0
    for sd in v.get("side_data_list", []):
        rot = int(sd.get("rotation", rot))
    return {
        "codec": v["codec_name"], "width": v["width"], "height": v["height"], "rotation": rot,
        "fps_num": num, "fps_den": den, "fps": num / den, "pix_fmt": v.get("pix_fmt"),
        "bit_depth": int(v.get("bits_per_raw_sample") or (10 if "10" in v.get("pix_fmt", "") else 8)),
        "color_space": v.get("color_space"), "color_transfer": v.get("color_transfer"),
        "color_primaries": v.get("color_primaries"), "color_range": v.get("color_range"),
        "duration": float(j["format"]["duration"]), "creation_time": j["format"].get("tags", {}).get("creation_time"),
        "audio": {"codec": a["codec_name"], "channels": a["channels"], "rate": int(a["sample_rate"])} if a else None,
        "tags": j["format"].get("tags", {}),
    }


def luma_stats(path, samples=24):
    """Average YMIN/YAVG/YMAX (as % of full 8-bit scale) over `samples` frames spread through the clip."""
    d = probe(path)["duration"]
    fps = max(samples / max(d, 1), 0.05)
    out = subprocess.run(["ffmpeg", "-v", "info", "-i", path, "-vf", f"fps={fps},scale=480:-2,signalstats,metadata=print",
                          "-an", "-f", "null", "-"], capture_output=True, text=True).stderr
    g = lambda k: [float(x) for x in re.findall(rf"lavfi\.signalstats\.{k}=([\d.]+)", out)]
    ymin, ymax, yavg = g("YLOW"), g("YHIGH"), g("YAVG")
    n = max(len(yavg), 1)
    return {"ylow_pct": 100 * sum(ymin) / n / 255, "yhigh_pct": 100 * sum(ymax) / n / 255, "yavg_pct": 100 * sum(yavg) / n / 255, "n": len(yavg)}


def classify(path):
    """Returns {'profile': ..., 'confidence': ..., 'reasons': [...]}. Profiles: rec709, hlg, pq, log_suspected."""
    p, reasons = probe(path), []
    tr = p["color_transfer"]
    if tr == "arib-std-b67":
        return {"profile": "hlg", "confidence": "high", "reasons": ["transfer=arib-std-b67"], "probe": p}
    if tr == "smpte2084":
        return {"profile": "pq", "confidence": "high", "reasons": ["transfer=smpte2084"], "probe": p}
    s = luma_stats(path)
    reasons.append(f"luma low/avg/high = {s['ylow_pct']:.0f}/{s['yavg_pct']:.0f}/{s['yhigh_pct']:.0f}%")
    # S-Log3 shot at base exposure sits low and flat: blacks lifted (~>= 9%), highlights rarely above ~75%, mean ~ 30-45%.
    flat = s["ylow_pct"] >= 8 and s["yhigh_pct"] <= 78
    tagged = tr in ("bt709", "iec61966-2-1") or p["color_space"] == "bt709"
    sony = any("sony" in str(v).lower() for v in p["tags"].values())
    if flat and not tagged:
        reasons.append("flat/lifted histogram and untagged transfer -> likely log")
        return {"profile": "log_suspected", "confidence": "medium", "reasons": reasons, "stats": s, "probe": p}
    if flat and tagged:
        reasons.append("tagged bt709 but histogram is flat: confirm with user/camera settings before any LUT")
        return {"profile": "rec709", "confidence": "low", "reasons": reasons, "stats": s, "probe": p}
    reasons.append(f"transfer={tr or 'untagged'}; normal contrast range -> Rec.709, do NOT apply a log->709 LUT" + (" (Sony tag present)" if sony else ""))
    return {"profile": "rec709", "confidence": "high" if tagged else "medium", "reasons": reasons, "stats": s, "probe": p}


if __name__ == "__main__":
    import sys
    print(json.dumps(classify(sys.argv[1]), indent=2, default=str))
