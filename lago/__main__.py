"""python -m lago <cmd>
  drive-ls ID | drive-find QUERY | drive-pull ID DEST | drive-push FILE PARENT_ID
  probe FILE | transcribe FILE OUT.json [model] | edit TRANSCRIPT.json SRC OUT_EDL.json | render EDL.json SRC OUT.mp4 [--lut X --lut-in rec709 --crop-x 0.5]
"""
import argparse, json, sys


def main():
    a = sys.argv[1:]
    if not a: print(__doc__); return
    c, rest = a[0], a[1:]
    if c == "drive-ls":
        from . import drive
        for f in drive.children(rest[0]): print(f["id"], f["mimeType"].split("/")[-1], f.get("size", "-"), f["modifiedTime"], f["name"])
    elif c == "drive-find":
        from . import drive
        for f in drive.search(rest[0]): print(f["id"], f.get("size", "-"), f["modifiedTime"], f["name"])
    elif c == "drive-pull":
        from . import drive; print(drive.download(rest[0], rest[1]))
    elif c == "drive-push":
        from . import drive; print(json.dumps(drive.upload(rest[0], rest[1], mime="video/mp4" if rest[0].endswith(".mp4") else "application/octet-stream")))
    elif c == "drive-rename":
        from . import drive; print(drive.rename(rest[0], rest[1])["name"])
    elif c == "drive-move":
        from . import drive; print(drive.move(rest[0], rest[1]))
    elif c == "drive-mkdir":
        from . import drive; print(drive.mkdir(rest[0], rest[1]))
    elif c == "probe":
        from .probe import classify; print(json.dumps(classify(rest[0]), indent=2, default=str))
    elif c == "transcribe":
        from .transcribe import transcribe; transcribe(rest[0], rest[1], *(rest[2:3] or ["small"]))
    elif c == "edit":
        from . import edit
        from .probe import probe
        tr = edit.load(rest[0]); p = probe(rest[1])
        e = edit.build_edl(tr, rest[1], p["fps"], p["duration"])
        e = edit.snap_to_silence(e, edit.flatten(tr)); edit.save(e, rest[2])
        open(rest[2].replace(".json", ".edl"), "w").write(edit.edl_cmx3600(e))
        print(f"{len(e['segments'])} segments, {len(e['dropped'])} dropped")
    elif c == "render":
        from .render import render
        from .probe import classify
        ap = argparse.ArgumentParser(); ap.add_argument("edl"); ap.add_argument("src"); ap.add_argument("out")
        ap.add_argument("--lut"); ap.add_argument("--lut-in"); ap.add_argument("--crop-x", type=float, default=0.5)
        o = ap.parse_args(rest)
        render(json.load(open(o.edl)), o.out, o.src, lut=o.lut, lut_in_profile=o.lut_in, profile=classify(o.src)["profile"], crop_x=o.crop_x)
    else: print(__doc__)


main()
