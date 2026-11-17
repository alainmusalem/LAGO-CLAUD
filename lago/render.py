"""EDL -> 1080x1920 H.264 MP4 with FFmpeg. Cuts only, optional LUT (colour-managed), uniform loudness, original FPS."""
import json, os, subprocess
from .probe import probe

TARGET_W, TARGET_H = 1080, 1920


def _lufs_pass1(src, segs, I=-16.0, TP=-1.5):
    a = "".join(f"[0:a]atrim={s['start']:.3f}:{s['end']:.3f},asetpts=PTS-STARTPTS[a{i}];" for i, s in enumerate(segs))
    a += "".join(f"[a{i}]" for i in range(len(segs))) + f"concat=n={len(segs)}:v=0:a=1,loudnorm=I={I}:TP={TP}:LRA=11:print_format=json[o]"
    err = subprocess.run(["ffmpeg", "-hide_banner", "-i", src, "-filter_complex", a, "-map", "[o]", "-f", "null", "-"], capture_output=True, text=True).stderr
    return json.loads(err[err.rindex("{"):err.rindex("}") + 1])


def video_chain(p, crop_x, lut, lut_in_profile, profile):
    """Crop to 9:16 (centre by default, crop_x 0..1 moves the window), scale, LUT, tag as Rec.709."""
    w, h = p["width"], p["height"]
    if p["rotation"] in (90, -90, 270): w, h = h, w
    f = []
    if w / h > TARGET_W / TARGET_H + 0.01:      # landscape/square -> crop to 9:16 window
        cw = int(round(h * TARGET_W / TARGET_H / 2)) * 2
        f.append(f"crop={cw}:{h}:(iw-{cw})*{crop_x}:0")
    f.append(f"scale={TARGET_W}:{TARGET_H}:flags=lanczos")
    if lut:
        if profile != lut_in_profile:
            raise SystemExit(f"LUT expects {lut_in_profile} input but footage is {profile}: refusing to apply (would damage colour).")
        f.append(f"lut3d=file='{lut}':interp=tetrahedral")
    f.append("format=yuv420p")
    return ",".join(f)


def render(edl, out, src_path, lut=None, lut_in_profile=None, profile="rec709", crop_x=0.5, crf=16, preset="slow", fade=0.012, I=-16.0):
    p = probe(src_path)
    segs = edl["segments"]
    n = len(segs)
    m = _lufs_pass1(src_path, segs, I=I) if p["audio"] else None
    vc = video_chain(p, crop_x, lut, lut_in_profile, profile)
    parts = []
    for i, s in enumerate(segs):
        d = s["end"] - s["start"]
        parts.append(f"[0:v]trim={s['start']:.3f}:{s['end']:.3f},setpts=PTS-STARTPTS[v{i}]")
        parts.append(f"[0:a]atrim={s['start']:.3f}:{s['end']:.3f},asetpts=PTS-STARTPTS,afade=t=in:d={fade},afade=t=out:st={max(d-fade,0):.3f}:d={fade}[a{i}]")
    parts.append("".join(f"[v{i}][a{i}]" for i in range(n)) + f"concat=n={n}:v=1:a=1[vc][ac]")
    parts.append(f"[vc]{vc}[vout]")
    ln = (f"loudnorm=I={I}:TP=-1.5:LRA=11:measured_I={m['input_i']}:measured_TP={m['input_tp']}:measured_LRA={m['input_lra']}"
          f":measured_thresh={m['input_thresh']}:offset={m['target_offset']}:linear=true") if m else "anull"
    parts.append(f"[ac]{ln},aresample=48000[aout]")
    cmd = ["ffmpeg", "-y", "-hide_banner", "-v", "warning", "-i", src_path, "-filter_complex", ";".join(parts), "-map", "[vout]", "-map", "[aout]",
           "-r", f"{p['fps_num']}/{p['fps_den']}", "-fps_mode", "cfr", "-c:v", "libx264", "-preset", preset, "-crf", str(crf), "-profile:v", "high",
           "-pix_fmt", "yuv420p", "-colorspace", "bt709", "-color_primaries", "bt709", "-color_trc", "bt709", "-color_range", "tv",
           "-c:a", "aac", "-b:a", "256k", "-movflags", "+faststart", out]
    subprocess.run(cmd, check=True)
    return out
