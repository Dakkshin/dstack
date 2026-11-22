"""Narration audio: one ElevenLabs take per scene, cut into one clip per beat.

    python tts.py <project_dir>

Each scene's beats are joined and spoken in a single request, so the delivery runs on from one
beat to the next the way a person talks, instead of restarting every sentence. The request
returns character timings, and the take is cut between beats in the middle of each pause, so
every beat still gets its own clip (audio/<beat>.mp3) for build.py to place at its beat's start.

Key: ELEVENLABS_API_KEY from the environment, else from <skill>/.env. Never printed.
Voice: VOICE_NAME or VOICE_ID in the project's narration.py. There is no default, because the
skill asks the person which voice to use before the first build.
Model: MODEL in narration.py, else ELEVENLABS_MODEL_ID, else eleven_multilingual_v2.
Takes are cached per scene in audio/<scene>.take.mp3 with a stamp of what made them, so only
scenes whose text or settings changed are re-synthesised. Without a key it writes estimated
durations so a silent preview can still be timed.
"""

import base64
import importlib.util
import json
import os
import re
import subprocess
import sys
from pathlib import Path

import requests

SKILL = Path(__file__).resolve().parent.parent
# Named voices, so a project asks for "matilda" instead of pasting an id. The skill asks the
# person to pick one and writes it into narration.py as VOICE_NAME. The notes come from each
# voice's ElevenLabs labels. jessica is a shared-library voice, so /v1/voices/<id> answers
# voice_not_found for it and its preview comes from /v1/shared-voices instead.
VOICES = {
    "mark": ("UgBBYS2sOqTuMpoF3BR0", "young male, American; casual and conversational"),
    "alex": ("SHJeg1jtED7EW6Zr6rHc", "middle-aged male, Canadian; calm, clear and friendly"),
    "will": ("bIHbv24MWmeRgasZH58o", "young male, American; relaxed and upbeat"),
    "matilda": ("XrExE9yKIg1WjnnlVkGX", "middle-aged female, American; knowledgeable, made for teaching"),
    "jessica": ("r1KmysJdVYZjJCm4mL3b", "female, shared library; playful, bright and warm"),
}
DEFAULT_MODEL = "eleven_v4"  # most expressive (Sept 2026); performs [audio tags] in the text
EXPRESSIVE = ("eleven_v3", "eleven_v4")  # models that perform tags; others would read them aloud
TAG = re.compile(r"\[[^\]]+\]\s*")


def expressive(model):
    return model.startswith(EXPRESSIVE)


def strip_tags(text):
    """The words alone: what script.md shows and what a non-expressive model is sent."""
    return re.sub(r"\s{2,}", " ", TAG.sub("", text)).strip()
WORDS_PER_SEC = 2.4  # silent estimate only
# Three delivery registers, chosen per scene (one take keeps one character all the way through):
#   A: widest pitch range and texture, for the opening scene
#   B: dynamic but softer, the default explaining voice
#   C: gentle and steady, for the closing scene
# Force one with a fourth element on the scene: ("S03_X", "Title", [...beats], "A").
REGISTERS = {
    "A": {"stability": 0.30, "similarity_boost": 0.85, "style": 0.35, "speed": 1.00},
    "B": {"stability": 0.42, "similarity_boost": 0.85, "style": 0.22, "speed": 1.00},
    "C": {"stability": 0.52, "similarity_boost": 0.80, "style": 0.12, "speed": 0.98},
}
# The expressive models take only these stability steps (creative, natural, robust). Tags
# respond best at natural or below. eleven_v3 also rejects previous_text / next_text.
V3_STABILITY = (0.0, 0.5, 1.0)


def scene_register(i, n, scene):
    if len(scene) > 3:
        return scene[3]
    return "A" if i == 0 else "C" if i == n - 1 else "B"


# ---------- lint: does the script read like speech? ----------

BUILTIN_BANNED = ("manage", "handle", "facilitate", "leverage", "seamless", "robust", "powerful",
                  "simply", "easily")
META = ("let's", "note that", "in summary", "in this section", "to summarize")


def style_file(nar):
    """The style guide to write narration by: STYLE in narration.py, else NARRATION_STYLE."""
    path = getattr(nar, "STYLE", "") or os.environ.get("NARRATION_STYLE", "")
    return Path(path).expanduser() if path else None


def banned_words(nar):
    f = style_file(nar)
    words = list(BUILTIN_BANNED)
    if f and f.exists() and f.suffix == ".json":
        try:
            for item in json.loads(f.read_text()).get("bannedInBothModes", []):
                words += [w.strip().lower() for w in re.split(r"[,/]", item.get("term", ""))
                          if re.fullmatch(r"[a-z ]+", w.strip().lower() or "-")]
        except (ValueError, AttributeError):
            pass
    return sorted(set(w for w in words if w and w not in META))


def lint(nar, model=DEFAULT_MODEL):
    """Warn about lines that read like text rather than speech. Never blocks the build."""
    banned = banned_words(nar)
    out = []
    for _, _, beats, *_ in nar.SCENES:
        for bid, raw, *_ in beats:
            text = strip_tags(raw)
            t = text.lower()
            why = []
            tags = TAG.findall(raw)
            if tags and not expressive(model):
                why.append(f"{len(tags)} tag(s) dropped: {model} would read them aloud")
            if len(tags) > 2:
                why.append(f"{len(tags)} tags in one beat (tags fight; keep to inflection points)")
            caps = re.findall(r"\b[A-Z]{2,}\b", text)
            caps = [c for c in caps if c not in ("GPU", "CPU", "RSA", "AI", "OK")]
            if len(caps) > 1:
                why.append(f"{len(caps)} capitalised words (one emphasis per beat)")
            if re.search(r"[\u2014\u2013\u2192\u00b7\u2264\u2265]", text):
                why.append("dash, arrow or symbol")
            if re.search(r"\w: \w", text):
                why.append("mid-sentence colon")
            why += [f"'{w}'" for w in META if w in t]
            why += [f"'{w}'" for w in banned if re.search(rf"\b{re.escape(w)}\b", t)]
            why += [f"'{m}' (contract it)" for m in
                    re.findall(r"\b(it is|that is|does not|do not|is not|can not|cannot|we will|you would)\b", t)]
            sents = [x for x in re.split(r"(?<=[.?!])\s+", text) if x]
            lens = [len(x.split()) for x in sents]
            why += [f"{n}-word sentence" for n in lens if n > 30]
            for a, b, c in zip(lens, lens[1:], lens[2:]):
                if max(a, b, c) - min(a, b, c) <= 3 and min(a, b, c) >= 8:
                    why.append("three sentences of the same length")
                    break
            if why:
                out.append(f"  {bid}: {', '.join(dict.fromkeys(why))}")
    if out:
        print("script lint (reads like text, not speech; see references/voice.md):")
        print("\n".join(out))
    else:
        print("script lint: ok")


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
    """VOICE_NAME, else VOICE_ID, from narration.py. Exits when neither is set.

    Returns (name, id). The name keeps the log and voice.json readable, the id is what goes on
    the wire, and the id is what the clip cache keys on, so switching voice re-synthesises.
    The environment is never consulted, so a stale .env can't pick a voice nobody asked for."""
    asked = (getattr(nar, "VOICE_NAME", "") or "").strip()
    raw = (getattr(nar, "VOICE_ID", "") or "").strip()
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
    sys.exit("no voice chosen: ask the person which voice to use, then set VOICE_NAME in "
             f"narration.py to one of: {', '.join(VOICES)}")


def previews(dest: Path):
    """Download each named voice's preview MP3 into dest. Costs no credits.

    The voice endpoints return a preview_url on ElevenLabs' public CDN, and fetching that file
    is free. Shared-library voices aren't on /v1/voices, so they fall back to a search of
    /v1/shared-voices by id."""
    load_env()
    key = os.environ.get("ELEVENLABS_API_KEY", "").strip()
    if not key:
        sys.exit("previews need ELEVENLABS_API_KEY in the skill's .env")
    h = {"xi-api-key": key}
    dest.mkdir(parents=True, exist_ok=True)
    for name, (vid, note) in VOICES.items():
        url = None
        r = requests.get(f"https://api.elevenlabs.io/v1/voices/{vid}", headers=h, timeout=30)
        if r.ok:
            url = r.json().get("preview_url")
        else:
            r = requests.get("https://api.elevenlabs.io/v1/shared-voices",
                             params={"search": vid, "page_size": 5}, headers=h, timeout=30)
            if r.ok:
                url = next((v.get("preview_url") for v in r.json().get("voices", [])
                            if v.get("voice_id") == vid), None)
        if not url:
            print(f"{name:<8} no preview found ({note})")
            continue
        out = dest / f"{name}.mp3"
        out.write_bytes(requests.get(url, timeout=60).content)
        print(f"{name:<8} {out}  ({note})")


def probe(path: Path) -> float:
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(path)],
        capture_output=True, text=True, check=True,
    )
    return float(out.stdout.strip())


def synth(text, prev, nxt, key, voice, model, settings):
    """One take with character timings. Returns (mp3 bytes, alignment dict)."""
    body = {"text": text, "model_id": model, "voice_settings": settings}
    if not model.startswith("eleven_v3"):
        body.update(previous_text=strip_tags(prev), next_text=strip_tags(nxt))
    r = requests.post(
        f"https://api.elevenlabs.io/v1/text-to-speech/{voice}/with-timestamps",
        params={"output_format": "mp3_44100_128"},
        headers={"xi-api-key": key},
        json=body,
        timeout=300,
    )
    if r.status_code != 200:
        sys.exit(f"ElevenLabs error {r.status_code}: {r.text[:300]}")
    j = r.json()
    return base64.b64decode(j["audio_base64"]), j.get("alignment") or j["normalized_alignment"]


def cut_points(beat_texts, alignment, total):
    """Seconds at which to cut a take into beats: the middle of the pause between each beat's
    last character and the next beat's first. Returns [0, c1, ..., total]."""
    chars = alignment["characters"]
    starts, ends = alignment["character_start_times_seconds"], alignment["character_end_times_seconds"]
    spoken = "".join(chars)
    cuts, pos = [0.0], 0
    for k, bt in enumerate(beat_texts[:-1]):
        a = spoken.find(bt.strip()[:12], pos)
        b = spoken.find(beat_texts[k + 1].strip()[:12], max(a, pos) + 1)
        if a < 0 or b < 0:
            sys.exit(f"could not find beat {k + 2} in the take's timings; check for symbols the "
                     "model rewrites (spell them out in the text)")
        last = b - 1
        while last > 0 and not chars[last].strip():
            last -= 1
        cuts.append((ends[last] + starts[b]) / 2)
        pos = b
    cuts.append(total)
    return cuts


def cut(src, a, b, dest):
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(src), "-ss", f"{a:.3f}",
                    "-to", f"{b:.3f}", "-c:a", "libmp3lame", "-b:a", "160k", str(dest)], check=True)


def settings_for(model, base):
    s = dict(base)
    if expressive(model):
        s["stability"] = min(V3_STABILITY, key=lambda v: abs(v - s["stability"]))
    return s


def main(project: Path):
    load_env()
    key = os.environ.get("ELEVENLABS_API_KEY", "").strip()
    nar = load_narration(project)
    voice_name, voice = resolve_voice(nar)
    model = getattr(nar, "MODEL", "") or os.environ.get("ELEVENLABS_MODEL_ID", DEFAULT_MODEL)
    (project / "voice.json").write_text(json.dumps({"name": voice_name, "id": voice, "model": model},
                                                   indent=1))
    print(f"voice: {voice_name} ({voice}), model: {model}", flush=True)
    lint(nar, model)
    say = (lambda t: t.strip()) if expressive(model) else strip_tags
    regs = {k: {**v, **getattr(nar, "VOICE", {})} for k, v in REGISTERS.items()}
    if os.environ.get("ELEVENLABS_SPEED"):
        for v in regs.values():
            v["speed"] = float(os.environ["ELEVENLABS_SPEED"])

    audio = project / "audio"
    audio.mkdir(exist_ok=True)
    scenes = nar.SCENES
    texts = [" ".join(say(b[1]) for b in sc[2]) for sc in scenes]
    plan, durations, all_real = {}, {}, True
    for i, sc in enumerate(scenes):
        sid, beats = sc[0], sc[2]
        reg = scene_register(i, len(scenes), sc)
        plan[sid] = reg
        settings = settings_for(model, regs[reg])
        take, stamp = audio / f"{sid}.take.mp3", audio / f"{sid}.take.txt"
        tag = json.dumps({"voice": voice, "model": model, "settings": settings,
                          "beats": [say(b[1]) for b in beats]}, sort_keys=True)
        fresh = take.exists() and stamp.exists() and stamp.read_text() == tag \
            and all((audio / f"{b[0]}.mp3").exists() for b in beats)
        if key and not fresh:
            print(f"tts {sid} [{reg}] ({len(texts[i])} chars)", flush=True)
            prev = texts[i - 1] if i else ""
            nxt = texts[i + 1] if i + 1 < len(texts) else ""
            data, align = synth(texts[i], prev, nxt, key, voice, model, settings)
            take.write_bytes(data)
            cuts = cut_points([say(b[1]) for b in beats], align, probe(take))
            for (bid, *_), a, b in zip(beats, cuts, cuts[1:]):
                cut(take, a, b, audio / f"{bid}.mp3")
            stamp.write_text(tag)
            fresh = True
        all_real &= fresh
        for bid, text, *_ in beats:
            clip = audio / f"{bid}.mp3"
            durations[bid] = probe(clip) if fresh else \
                round(len(strip_tags(text).split()) / WORDS_PER_SEC + 0.3, 2)
    (project / "registers.json").write_text(json.dumps(plan, indent=1))
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
    if len(sys.argv) > 1 and sys.argv[1] in ("--previews", "previews"):
        previews(Path(sys.argv[2] if len(sys.argv) > 2 else "voice-previews").resolve())
        sys.exit(0)
    main(Path(sys.argv[1]).resolve())
