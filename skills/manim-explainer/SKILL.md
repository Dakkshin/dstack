---
name: manim-explainer
description: Make a narrated 3Blue1Brown-style explainer video with Manim Community Edition and ElevenLabs voice, synced beat by beat and merged to a 1080p60 MP4. Use whenever someone wants an animated maths, CS, crypto or algorithm explainer, a "3b1b style" video, a Manim animation with voiceover, or a study/viva/lecture video on a technical topic, even if they don't name Manim.
---

# Manim explainer

Builds a narrated explainer from three project files. The engine in `scripts/` handles beat
sync, TTS, rendering, audio placement and the visual overlap check. Start every project by
copying `templates/project/`, which is a two-scene starter that shows the whole contract in about
100 lines and carries no topic of its own.

`examples/rsa/` is a full worked video about RSA (11 scenes, about 7.5 minutes, roughly 66 KB).
Do not read it whole and do not borrow its content. When you need one technique the starter
doesn't show, such as a sidebar of running results or a morphing equation, grep for it
(`grep -n "TransformMatchingTex\|always_redraw" "$MK/examples/rsa/scenes.py"`) and read only
those lines.

## Where the skill lives

The folder holding this file is the skill folder, and every command below calls it `$MK`. It has
one home, which is `~/projects/dstack/skills/manim-explainer` inside the dstack plugin, and each
app reaches that same folder in its own way: an app that loads dstack as a plugin sees it as `dstack:manim-explainer`,
`~/.agents/skills/manim-explainer` is a symlink to it, pi reads
`~/.agents/skills` directly, and Antigravity reads it through `~/.gemini/config/skills` (which
points at `~/.agents/skills`) as well as `~/.gemini/antigravity/skills` and
`~/.gemini/antigravity-cli/skills`. Resolve it once per session and use `$MK` from then on:

```bash
for d in ~/.agents/skills/manim-explainer ~/projects/dstack/skills/manim-explainer ~/.gemini/config/skills/manim-explainer .agents/skills/manim-explainer; do [ -f "$d/SKILL.md" ] && MK=$d && break; done; echo "$MK"
```

A workspace skill sits at `.agents/skills/manim-explainer` inside the project, and that last path
in the list picks it up. `.venv` keeps working through any of those paths because Python resolves
the real directory before it looks for `pyvenv.cfg`. Copying the folder somewhere else breaks the
venv, so run `setup.sh` again at the new path if you ever move it for real.

## Setup (once per machine)

`"$MK/setup.sh"` creates `.venv` with Manim, checks ffmpeg and LaTeX, and copies `.env.example`
to `.env`. The ElevenLabs key lives in `.env` here (`ELEVENLABS_API_KEY`, plus
`ELEVENLABS_VOICE`, the named voice the section below covers). `tts.py` reads it. Never print it,
echo it or copy it into a project.

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
  `TITLE`, `OUTPUT_NAME`, `INTRO`, `SOURCES`. Use f-strings over `numbers.json` so the voice and
  the screen can't disagree. Write numbers the way they should be spoken. Spell out symbols
  ("m to the e, mod n") and avoid long binary strings.
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

## Build loop

```bash
PY="$MK/.venv/bin/python"
B="$MK/scripts/build.py"
$PY $B <project> preview          # 480p15, real narration if the key is set
$PY $B <project> preview S04 S05  # re-render only these (no assembly)
$PY $B <project> final            # 1080p60 -> OUTPUT_NAME, refuses without real narration
```

Each build runs compute.py, then TTS (cached per beat, so only changed text is re-synthesised),
then writes script.md, renders scenes 6 at a time, concatenates them, and places every clip at
its beat's logged start time.

## Visual check (required before final)

After a preview, `check/sheet_<Scene>.png` tiles one frame from the end of each beat. Read
every sheet and fix anything that overlaps, is clipped at the frame edge, is too small, or has
arrows crossing boxes. Then rebuild and recheck the frames you changed. Common fixes are in
`references/style.md`.

## Style rules

Read `references/style.md` for the palette, layout safe area and animation conventions.

## Gotchas

- Parallel renders each get their own LaTeX cache (`media/Tex/<Scene>`). A shared cache
  corrupts SVGs ("does not support converting .dvi files to SVG").
- `TransformMatchingTex` matches whole MathTex arguments. Split equations into the parts you
  want to morph (`M("c^{d}", "=", "m^{ed}")`).
- Use `fmt(x)` for thousands separators inside MathTex.
- Audio sync comes from `timings/<Scene>.json`, which is logged at render time. Never hand-edit it.
- The voice is per project (`VOICE_NAME`, see "Pick the voice"). Change it and the whole
  narration re-synthesises, which costs credits; say so before you switch one mid-project.
- Delivery moves between three registers per beat (`REGISTERS` in tts.py). A is the widest range, for hooks, questions and punchlines. B is dynamic but softer, for explaining. C is gentle, for number walkthroughs and the recap. `pick_register` chooses from the text and never repeats one three times in a row. To force a beat, write `("id", "text", "A")`. The plan is written to `<project>/registers.json`. A `VOICE = {...}` in narration.py overrides keys in all three. Changing settings re-synthesises the affected clips.
- At these settings ElevenLabs runs about 2.5 words per second. Target ~1,000 words for 7 minutes.
