"""Build a narrated Manim explainer.

    python build.py <project_dir> preview            # 480p15 + check/ frames per beat
    python build.py <project_dir> final              # 1080p60 with narration
    python build.py <project_dir> preview S03 S04    # re-render only these scenes, then stop

Project layout: compute.py (optional, writes numbers.json), narration.py (SCENES, optional
TITLE / OUTPUT_NAME / INTRO / SOURCES), scenes.py (SCENE_ORDER + ExplainerScene subclasses).
"""

import importlib.util
import json
import os
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

SKILL_SCRIPTS = Path(__file__).resolve().parent
sys.path.insert(0, str(SKILL_SCRIPTS))
import tts  # noqa: E402

PY = sys.executable
QUAL = {"preview": ("l", "480p15"), "final": ("h", "1080p60")}


def probe(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                          "-of", "csv=p=0", str(path)], capture_output=True, text=True, check=True)
    return float(out.stdout.strip())


def scene_order(project):
    src = (project / "scenes.py").read_text()
    start = src.index("SCENE_ORDER")
    return eval(src[src.index("[", start):src.index("]", start) + 1])


def write_script(project, nar):
    lines = [f"# {getattr(nar, 'TITLE', 'Narration script')}", ""]
    if getattr(nar, "INTRO", ""):
        lines += [nar.INTRO, ""]
    for i, (_, title, beats) in enumerate(nar.SCENES, 1):
        lines += [f"## {i}. {title}", ""] + [b[1] for b in beats] + [""]
    if getattr(nar, "SOURCES", None):
        lines += ["## Sources", ""] + [f"- {s}" for s in nar.SOURCES] + [""]
    (project / "script.md").write_text("\n".join(lines))


def render(project, scene, q):
    log = project / "logs" / f"{scene}.log"
    log.parent.mkdir(exist_ok=True)
    env = dict(os.environ, EXPLAINER_LIB=str(SKILL_SCRIPTS),
               EXPLAINER_TEX_DIR=str(project / "media" / "Tex" / scene))
    with open(log, "w") as f:
        r = subprocess.run([PY, "-m", "manim", "render", f"-q{q}", "--disable_caching",
                            "--progress_bar", "none", "scenes.py", scene],
                           cwd=project, stdout=f, stderr=subprocess.STDOUT, env=env)
    return scene, r.returncode


def ff(*args):
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", *map(str, args)], check=True)


def main():
    project = Path(sys.argv[1]).resolve()
    mode = sys.argv[2] if len(sys.argv) > 2 else "preview"
    only = sys.argv[3:]
    q, folder = QUAL[mode]

    if (project / "compute.py").exists():
        subprocess.run([PY, "compute.py"], cwd=project, check=True)
    source = tts.main(project)
    nar = tts.load_narration(project)
    write_script(project, nar)
    if mode == "final" and source != "elevenlabs":
        sys.exit("final needs real narration: put ELEVENLABS_API_KEY in the skill's .env")

    order = scene_order(project)
    with ThreadPoolExecutor(max_workers=6) as ex:
        failed = []
        for scene, rc in ex.map(lambda s: render(project, s, q), only or order):
            print(f"render {scene}: {'ok' if rc == 0 else 'FAILED (logs/' + scene + '.log)'}", flush=True)
            if rc:
                failed.append(scene)
    if failed:
        sys.exit(1)
    if only:
        return

    vids = [project / "media" / "videos" / "scenes" / folder / f"{s}.mp4" for s in order]
    lst = project / "logs" / "concat.txt"
    lst.write_text("".join(f"file '{v}'\n" for v in vids))
    silent = project / f"video_{mode}.mp4"
    ff("-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", silent)

    placements, offset, scene_of = [], 0.0, {}
    for s, v in zip(order, vids):
        t = json.loads((project / "timings" / f"{s}.json").read_text())
        for bid, start in t["beats"].items():
            placements.append((bid, offset + start))
            scene_of[bid] = s
        offset += probe(v)

    out = project / (getattr(nar, "OUTPUT_NAME", "explainer.mp4") if mode == "final" else "preview.mp4")
    if source == "elevenlabs":
        cmd = ["-i", silent]
        for bid, _ in placements:
            cmd += ["-i", project / "audio" / f"{bid}.mp3"]
        parts = [f"[{i + 1}:a]aresample=48000,adelay={int(at * 1000)}:all=1[a{i}]"
                 for i, (_, at) in enumerate(placements)]
        mix = "".join(f"[a{i}]" for i in range(len(placements)))
        fc = ";".join(parts) + (f";{mix}amix=inputs={len(placements)}:normalize=0:dropout_transition=0,"
                                "loudnorm=I=-16:TP=-1.5:LRA=11[aout]")
        ff(*cmd, "-filter_complex", fc, "-map", "0:v", "-map", "[aout]", "-c:v", "copy",
           "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-t", f"{offset:.3f}",
           "-movflags", "+faststart", out)
    else:
        ff("-i", silent, "-c", "copy", out)
    print(f"wrote {out}: {offset / 60:.2f} min, narration={'yes' if source == 'elevenlabs' else 'no'}")

    # overlap/clipping review: one frame at the end of each beat, tiled per scene
    chk = project / "check"
    chk.mkdir(exist_ok=True)
    for old in chk.glob("*.png"):
        old.unlink()
    beats = json.loads((project / "durations.json").read_text())["beats"]
    for bid, at in placements:
        ff("-ss", f"{at + beats[bid] + 0.2:.2f}", "-i", out, "-frames:v", "1",
           "-vf", "scale=640:-1", chk / f"{scene_of[bid]}__{bid}.png")
    beat_ids = [b for b, _ in placements]
    for s in order:
        frames = sorted(chk.glob(f"{s}__*.png"), key=lambda p: beat_ids.index(p.stem.split("__")[1]))
        sheet = chk / f"sheet_{s}.png"
        if len(frames) == 1:
            ff("-i", frames[0], sheet)
            continue
        # 2 columns: x is 0 or w0, y is 0, h0, h0+h0, ...
        layout = "|".join(f"{'w0' if i % 2 else 0}_{'+'.join(['h0'] * (i // 2)) or 0}"
                          for i in range(len(frames)))
        inputs = sum([["-i", f] for f in frames], [])
        ff(*inputs, "-filter_complex", f"xstack=inputs={len(frames)}:layout={layout}:fill=gray", sheet)
    print(f"check sheets: {chk}/sheet_*.png")


if __name__ == "__main__":
    main()
