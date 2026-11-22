---
name: manim-explainer
description: Make a narrated 3Blue1Brown-style explainer video with Manim Community Edition and ElevenLabs voice, synced beat by beat and merged to a 1080p60 MP4. Use whenever someone wants an animated maths, CS, crypto or algorithm explainer, a "3b1b style" video, a Manim animation with voiceover, or a study/viva/lecture video on a technical topic, even if they don't name Manim.
---

# Manim explainer

Builds a narrated explainer from three project files. The engine in `scripts/` handles beat
sync, TTS, rendering, audio placement, a motion check and the visual overlap check. Start every
project by copying `templates/project/`, which is a two-scene starter that shows the whole
contract in about 80 lines and carries no topic of its own.

**Read `references/style.md` before writing any scene.** Its one rule is the difference
between a 3Blue1Brown video and animated slides: change what is on screen (move, morph,
rescale, zoom, dim) instead of fading new things in and clearing the stage. It was distilled
from Grant Sanderson's own scene code (github.com/3b1b/videos, CC BY-NC-SA, so the skill
describes his techniques and does not copy his code).

`examples/online-softmax/` is the worked example to learn from (7 scenes, about 5 minutes).
It shows trackers driving bars and a stacked total, a curve drawn up to a moving dot, the
camera pulling out over a long array and pushing in on a detail, equations morphing piece by
piece, and copies flying into a derived formula. Do not read it whole and do not borrow its
content. Grep for the technique you need
(`grep -n "always_redraw\|self.focus\|TransformFromCopy" "$MK/examples/online-softmax/scenes.py"`)
and read only those lines. `examples/rsa/` is an older video in the slide style the motion
check now flags; use it only for its sidebar and icon helpers.

## Where the skill lives

The folder holding this file is the skill folder, and every command below calls it `$MK`. It has
one home, which is `~/projects/studyskills/skills/manim-explainer` inside the studyskills plugin, and each
app reaches that same folder in its own way: an app that loads studyskills as a plugin sees it as `studyskills:manim-explainer`,
`~/.agents/skills/manim-explainer` is a symlink to it, pi reads
`~/.agents/skills` directly, and Antigravity reads it through `~/.gemini/config/skills` (which
points at `~/.agents/skills`) as well as `~/.gemini/antigravity/skills` and
`~/.gemini/antigravity-cli/skills`. Resolve it once per session and use `$MK` from then on:

```bash
for d in ~/.agents/skills/manim-explainer ~/projects/studyskills/skills/manim-explainer ~/.gemini/config/skills/manim-explainer .agents/skills/manim-explainer; do [ -f "$d/SKILL.md" ] && MK=$d && break; done; echo "$MK"
```

A workspace skill sits at `.agents/skills/manim-explainer` inside the project, and that last path
in the list picks it up. `.venv` keeps working through any of those paths because Python resolves
the real directory before it looks for `pyvenv.cfg`. Copying the folder somewhere else breaks the
venv, so run `setup.sh` again at the new path if you ever move it for real.

## Setup (once per machine)

`"$MK/setup.sh"` creates `.venv` with Manim, checks ffmpeg and LaTeX, and copies `.env.example`
to `.env`. The ElevenLabs key lives in `.env` here (`ELEVENLABS_API_KEY`). `tts.py` reads it.
Never print it, echo it or copy it into a project. `.env` may also set `NARRATION_STYLE`, which
is the path to the owner's writing style guide (see "Write the narration").

LaTeX: Arch needs `texlive-basic texlive-latex texlive-latexrecommended texlive-fontsrecommended
texlive-binextra`. `standalone.cls` (texlive-latexextra) is optional. The lib falls back to an
`article` template when it is missing.

## Pick the voice (always ask, never assume)

Five named voices are wired into `tts.py`. The build has no default and stops with
`no voice chosen` until the project's `narration.py` names one.

| name | character |
|---|---|
| `mark` | young male, American, casual and conversational |
| `alex` | middle-aged male, Canadian, calm, clear and friendly |
| `will` | young male, American, relaxed and upbeat |
| `matilda` | middle-aged female, American, knowledgeable and made for teaching |
| `jessica` | female, playful, bright and warm |

As soon as this skill is invoked, and before any build, ask the person which voice to use.

1. Ask one question with exactly four options, which are Mark, Alex, Will and Matilda, each
   with its one-line character from the table. Use the question tool when you have one. Say in
   the question that Jessica is also available, and that they can hear previews first.
2. If they want previews, download them. This calls the free voice-listing endpoints and
   fetches each voice's static sample from ElevenLabs' public CDN, so it costs no credits.

   ```bash
   "$MK/.venv/bin/python" "$MK/scripts/tts.py" --previews <project>/voice-previews
   ```

   Give them the five MP3 paths it prints so they can play them, then ask again.
3. Write the answer into `narration.py` as `VOICE_NAME = "<name>"`.

Ask once per project, not per beat, and never pick on their behalf. Nothing in the build can
tell the voices apart, and the same script reads differently in each. `build.py` then prints
`voice: <name> (<id>)` and writes `voice.json` into the project so the choice is on the record.

Switching the voice on an existing project re-synthesises every clip, because the clip cache is
keyed on the voice id. The images do not change, so only the audio and the assembly redo.

A voice that is not in the table still works if the person gives you its id. Put
`VOICE_ID = "<id>"` in `narration.py`. The environment and `.env` are never read for the voice.
A shared-library voice, such as `jessica`, can synthesise while `/v1/voices/<id>` answers
`voice_not_found`, so test an unfamiliar id with a short sentence before building the whole
project.

## Project layout

Make a project dir with `cp -r "$MK/templates/project" ./videos/<topic>`, then replace the
placeholder content in each file:

- `compute.py`: computes every number shown or spoken and writes `numbers.json`, with asserts.
  Never type a number from memory into a scene or the narration. Read it from `numbers.json`.
  Historical facts (dates, records) are fixed values here and get cited in `SOURCES`.
- `narration.py`: `SCENES = [(scene_class, title, [(beat_id, text), ...]), ...]`. Optional
  `TITLE`, `OUTPUT_NAME`, `INTRO`, `SOURCES`, `MODEL`, `STYLE`. Use f-strings over
  `numbers.json` so the voice and the screen can't disagree. Write numbers the way they should
  be spoken. Spell out symbols ("m to the e, mod n") and avoid long binary strings. Write it by
  the next section.
- `scenes.py`: starts with

  ```python
  import os, sys
  sys.path.insert(0, os.environ.get("EXPLAINER_LIB") or "<paste $MK here>/scripts")
  from explainer_lib import *
  ```

  `build.py` sets `EXPLAINER_LIB` for every render, so the literal path only matters for your
  editor and for a `manim render` you run by hand.

  then one `ExplainerScene` subclass per scene plus `SCENE_ORDER = [...]`. Inside `construct`,
  wrap each narration beat in `with self.beat("id") as b:` and size run_times with
  `b.frac(0.3)` (a fraction of that clip's length). The beat waits out the rest of the clip on
  exit, so never pad with manual waits for audio.

  `ExplainerScene` is a `MovingCameraScene`, and the lib adds what Manim CE lacks for this
  style:

  | helper | does |
  |---|---|
  | `self.focus(mob)`, `self.home()` | camera push-in on a detail and back (animations; pass to `play`) |
  | `self.frame` | the camera frame, for any other move (`self.frame.animate.set(width=40)`) |
  | `self.pin(mob)` | keeps a HUD element fixed on screen while the camera moves |
  | `live_number(get)`, `live_bars(get_values)` | readouts and bar charts redrawn every frame from trackers |
  | `axes(...)`, `plane()` | axes and a NumberPlane in house style |
  | `during(anim, start, end, total)` | run one animation inside a window of a longer `play` |
  | `flash_around`, `box_then_fade`, `dim`, `backstroke` | emphasis that leaves nothing behind, dimming instead of removing, legible labels |

## Write the narration

Read `references/voice.md` first. If `NARRATION_STYLE` is set in `$MK/.env` (or `STYLE` in the
project's `narration.py`), read that style guide too and write in its plain, spoken mode. It
decides the wording, and `voice.md` decides the delivery.

The short version:
- Shape each scene as a spoken paragraph. Open with a reset (a discourse marker such as
  "So" or "Now", a question, or a lifting tag), explain on a steady line, and settle at the end.
- Put a few audio tags (`[curious]`, `[thoughtful]`, `[amused]`...) at the turning points,
  at most 2 per beat.
- Stress one new word per beat in CAPS, and use an ellipsis before a turn.
- End on the point said once more and more sharply, never on a recap card.

`tts.py` prints a script lint before every synthesis. Clear its warnings unless you have a
reason not to.

How the audio is made: each scene is one take on `eleven_v4` (set `MODEL` to change it), which
performs the tags. The take is cut into one clip per beat in the middle of its natural pauses,
so the delivery flows across beats while every beat still syncs to its animation. Changing one
beat re-voices only its scene. `eleven_multilingual_v2` is steadier but flatter, and it would
read tags aloud, so tags are stripped for it.

## Build loop

```bash
PY="$MK/.venv/bin/python"
B="$MK/scripts/build.py"
$PY $B <project> preview          # 480p15, real narration if the key is set
$PY $B <project> preview S04 S05  # re-render only these (no assembly)
$PY $B <project> final            # 1080p60 -> OUTPUT_NAME, refuses without real narration
```

Each build runs compute.py, then TTS (cached per beat, so only changed text is re-synthesised),
then writes script.md, prints the motion check, renders scenes 6 at a time, concatenates them,
and places every clip at its beat's logged start time.

The motion check counts entrances (`FadeIn`, `Write`, `Create`...) against motion (transforms,
`.animate`, trackers, updaters, camera moves) in each scene class and names any scene that is
mostly entrances. Treat a named scene as a slide to redesign, not a warning to ignore: find what
already on screen should move or change to carry that beat.

## Visual check (required before final)

After a preview, `check/sheet_<Scene>.png` tiles one frame from the end of each beat. Read
every sheet and fix anything that overlaps, is clipped at the frame edge, is too small, or has
arrows crossing boxes. Then rebuild and recheck the frames you changed. Common fixes are in
`references/style.md`.

End-of-beat frames miss what happens mid-motion, such as a zoom that crops a changing readout
or a moving label that crosses another. For each camera move and big tracker sweep, pull a
frame from the middle of it and look at that too:
`ffmpeg -ss <seconds> -i <project>/media/videos/scenes/480p15/<Scene>.mp4 -frames:v 1 mid.png`
(beat start times are in `timings/<Scene>.json`).

## Style rules

Read `references/style.md` for the motion rule, palette, layout safe area and timing.

## Gotchas

- Parallel renders each get their own LaTeX cache (`media/Tex/<Scene>`). A shared cache
  corrupts SVGs ("does not support converting .dvi files to SVG").
- `TransformMatchingTex` matches whole MathTex arguments by their exact text. Split equations
  into the parts you want to morph. CE 0.22 can split anywhere, including inside a fraction
  (`M(r"\frac{", "e^{x_i}", "}{", r"\sum_j e^{x_j}", "}")`) or a superscript.
- `always_redraw` objects keep updating until something stops them, and a redraw during a fade
  can crash a 1080p render that passed at 480p. `clear_stage()` freezes what it fades. Anything
  you fade or transform yourself, call `clear_updaters()` on it first.
- Use `fmt(x)` for thousands separators inside MathTex.
- Audio sync comes from `timings/<Scene>.json`, which is logged at render time. Never hand-edit it.
- The voice is per project (`VOICE_NAME`, see "Pick the voice"). Change it and the whole
  narration re-synthesises, which costs credits; say so before you switch one mid-project.
- Voice settings are chosen per scene (`REGISTERS` in tts.py), because one take keeps one
  character throughout. A is for the opening scene, C for the closing one and B for the rest,
  and a fourth element on a scene forces one (`("S03_X", "Title", [...], "A")`). On the
  expressive models, stability snaps to 0, 0.5 or 1, and tags do the expressive work, not the
  sliders. A `VOICE = {...}` in narration.py overrides keys in all three. The plan is written
  to `<project>/registers.json`.
- `eleven_v3` rejects `previous_text`/`next_text`, so `tts.py` sends them only to models that
  accept them.
- If a take can't be cut ("could not find beat N"), the model rewrote some characters. Spell
  out symbols in that beat.
- `build.py` prints `overruns`, which are beats whose animation outlasts the line and leaves
  dead air. Trim run_times in those beats.
- Narration runs about 2.5 words per second. Target ~1,000 words for 7 minutes.
