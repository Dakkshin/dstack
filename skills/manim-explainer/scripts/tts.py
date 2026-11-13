"""One ElevenLabs narration clip per beat.

    python tts.py <project_dir>

Key: ELEVENLABS_API_KEY from the environment, else from <skill>/.env. Never printed.
Voice: ELEVENLABS_VOICE_ID (env or .env), else the default below.
Clips are cached in <project>/audio/<beat>.mp3 next to a .txt of the text they were made
from, so only changed beats are re-synthesised. Without a key it writes estimated
durations so a silent preview can still be timed.
"""

import importlib.util
import json
import os
import subprocess
import sys
from pathlib import Path

import requests

SKILL = Path(__file__).resolve().parent.parent
# Named voices, so a project asks for "dax" instead of pasting an id. Pick one in
# narration.py (`VOICE_NAME`), which is what the skill asks for before the first build.
VOICES = {
    "dax": ("luatDliq6kNyK0iDnpTS", "default; cloned, young, en-indian"),
    "karpathy": ("whMcAwVxjECAijwDw09I", "cloned; drier, more technical"),
}
DEFAULT_VOICE_NAME = "dax"
DEFAULT_MODEL = "eleven_multilingual_v2"
WORDS_PER_SEC = 2.4  # silent estimate only
# Three delivery registers. Real speech moves between them, so each beat picks one from its
# content (see pick_register) instead of the whole video sitting on one setting.
#   A: widest pitch range and texture, for hooks, questions and punchlines
#   B: dynamic but softer, the default explaining voice
#   C: gentle and steady, for number walkthroughs and the recap
REGISTERS = {
    "A": {"stability": 0.30, "similarity_boost": 0.85, "style": 0.35, "speed": 1.00},
    "B": {"stability": 0.42, "similarity_boost": 0.85, "style": 0.22, "speed": 1.00},
    "C": {"stability": 0.52, "similarity_boost": 0.80, "style": 0.12, "speed": 0.98},
}
PUNCH_WORDS = ("not secure", "breaks", "attacker", "instant", "hopeless", "stuck", "verified",
               "a detail", "that is rsa", "the trick", "the real threat")


def pick_register(text, first_in_scene, numeric_scene_end, prev_two):
    """A for questions, scene openers and punchy lines; C for number-heavy steps; else B.

    Never three of the same register in a row, so the delivery keeps moving."""
    t = text.lower()
    digits = sum(ch.isdigit() for ch in text)
    words = len(text.split())
    if "?" in text or any(w in t for w in PUNCH_WORDS) or (first_in_scene and words < 30):
        r = "A"
    elif digits >= 10 or numeric_scene_end:
        r = "C"
    else:
        r = "B"
    if prev_two == [r, r]:
        r = "B" if r != "B" else ("A" if "?" in text or first_in_scene else "C")
    return r

def load_env():
    env = SKILL / ".env"
    if not env.exists():
        return
    for line in env.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        k = k.removeprefix("export ").strip()
        os.environ.setdefault(k, v.strip().strip('"').strip("'"))


def load_narration(project: Path):
    spec = importlib.util.spec_from_file_location("narration", project / "narration.py")
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def resolve_voice(nar):
    """narration.py VOICE_NAME/VOICE_ID, then ELEVENLABS_VOICE/ELEVENLABS_VOICE_ID, then dax.

    Returns (name, id). The name keeps the log and voice.json readable, the id is what goes on
    the wire, and the id is what the clip cache keys on, so switching voice re-synthesises."""
    asked = (getattr(nar, "VOICE_NAME", "") or os.environ.get("ELEVENLABS_VOICE", "")).strip()
    raw = (getattr(nar, "VOICE_ID", "") or os.environ.get("ELEVENLABS_VOICE_ID", "")).strip()
    if asked:
        if asked.lower() in VOICES:
            key = asked.lower()
            return key, VOICES[key][0]
        if len(asked) >= 20:  # a raw id dropped into VOICE_NAME
            return asked[:8], asked
        sys.exit(f"unknown voice {asked!r}; pick one of: {', '.join(VOICES)}")
    if raw:
        for key, (vid, _) in VOICES.items():
            if vid == raw:
                return key, raw
        return raw[:8], raw
    return DEFAULT_VOICE_NAME, VOICES[DEFAULT_VOICE_NAME][0]


def probe(path: Path) -> float:
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(path)],
        capture_output=True, text=True, check=True,
    )
    return float(out.stdout.strip())


def synth(text, prev, nxt, dest: Path, key, voice, model, settings):
    r = requests.post(
        f"https://api.elevenlabs.io/v1/text-to-speech/{voice}",
        params={"output_format": "mp3_44100_128"},
        headers={"xi-api-key": key, "accept": "audio/mpeg"},
        json={
            "text": text,
            "model_id": model,
            "previous_text": prev,
            "next_text": nxt,
            "voice_settings": settings,
        },
        timeout=120,
    )
    if r.status_code != 200:
        sys.exit(f"ElevenLabs error {r.status_code} on {dest.name}: {r.text[:300]}")
    dest.write_bytes(r.content)


def main(project: Path):
    load_env()
    key = os.environ.get("ELEVENLABS_API_KEY", "").strip()
    nar = load_narration(project)
    voice_name, voice = resolve_voice(nar)
    model = os.environ.get("ELEVENLABS_MODEL_ID", DEFAULT_MODEL)
    (project / "voice.json").write_text(json.dumps({"name": voice_name, "id": voice}, indent=1))
    print(f"voice: {voice_name} ({voice})", flush=True)
    regs = {k: {**v, **getattr(nar, "VOICE", {})} for k, v in REGISTERS.items()}
    if os.environ.get("ELEVENLABS_SPEED"):
        for v in regs.values():
            v["speed"] = float(os.environ["ELEVENLABS_SPEED"])
    flat, plan, recent = [], {}, []
    for sid, _, beats in nar.SCENES:
        recap = "recap" in sid.lower()
        for j, beat in enumerate(beats):
            bid, text = beat[0], beat[1]
            # a beat can force its register: ("id", "text", "A")
            r = beat[2] if len(beat) > 2 else pick_register(text, j == 0, recap and j > 0, recent[-2:])
            flat.append((bid, text))
            plan[bid] = r
            recent.append(r)
    audio = project / "audio"
    audio.mkdir(exist_ok=True)
    (project / "registers.json").write_text(json.dumps(plan, indent=1))
    durations = {}
    for i, (bid, text) in enumerate(flat):
        dest, stamp = audio / f"{bid}.mp3", audio / f"{bid}.txt"
        settings = regs[plan[bid]]
        tag = f"{voice}|{json.dumps(settings, sort_keys=True)}|{text}"
        fresh = dest.exists() and stamp.exists() and stamp.read_text() == tag
        if key and not fresh:
            print(f"tts {bid} [{plan[bid]}]", flush=True)
            prev = flat[i - 1][1] if i else ""
            nxt = flat[i + 1][1] if i + 1 < len(flat) else ""
            synth(text, prev, nxt, dest, key, voice, model, settings)
            stamp.write_text(tag)
            fresh = True
        durations[bid] = probe(dest) if fresh else round(len(text.split()) / WORDS_PER_SEC + 0.3, 2)
    all_real = all((audio / f"{b}.txt").exists() and (audio / f"{b}.txt").read_text()
                   == f"{voice}|{json.dumps(regs[plan[b]], sort_keys=True)}|{t}" for b, t in flat)
    source = "elevenlabs" if all_real else "estimate"
    (project / "durations.json").write_text(json.dumps({"source": source, "beats": durations}, indent=2))
    print(f"durations.json: {len(durations)} beats, {sum(durations.values()) / 60:.1f} min ({source})")
    return source


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] in ("--voices", "voices", "--list-voices"):
        pad = max(len(k) for k in VOICES)
        for key, (vid, note) in VOICES.items():
            print(f"{key:<{pad}}  {vid}  {note}")
        sys.exit(0)
    main(Path(sys.argv[1]).resolve())
