# Style reference

## The one rule: change what is on screen, don't replace it

A slide deck says "here is a thing" over and over. A 3Blue1Brown video says "watch this thing
become that one". In Grant Sanderson's own scene code (github.com/3b1b/videos, 2022-2025) there
are about 8,300 `play` calls and only about 44 places that clear the screen. Everything else
moves, morphs, rescales, dims or reframes something the viewer is already looking at, so the
eye never has to re-find its place, and the motion itself carries the explanation.

So, for every beat, ask: what on screen already relates to this idea, and how does it change?

| the idea is... | show it as... | tools |
|---|---|---|
| a quantity that changes | the bar, dot, needle or label driven by one tracker, moving continuously | `ValueTracker`, `always_redraw`, `live_number`, `live_bars` |
| one form becomes another | the same pieces sliding into place, new parts appearing | `TransformMatchingTex`, `TransformMatchingShapes`, `FadeTransform` |
| a result derived from parts | a copy flying out of the source into the new place | `TransformFromCopy(src, dst, path_arc=...)` |
| a function, rate or growth | a curve drawn up to a tracker, with a dot riding it | `axes()`, `axes.plot`, `Dot` in `always_redraw` |
| a mapping of space | the whole grid moving | `plane()`, `ApplyMatrix`, `ApplyPointwiseFunction` |
| scale ("a hundred thousand of these") | the camera pulling out over many copies, then back | `self.frame.animate.set(width=..)`, `self.home()` |
| a detail inside a picture | the camera pushing in, with context still in frame | `self.focus(target)` |
| "this, not that" | the rest dimmed, not removed | `dim(*mobs)` |
| a set of similar items | a wave, not all at once | `LaggedStart(..., lag_ratio=0.1)` |

Entrances (`FadeIn`, `Write`, `Create`) are still needed, but they only introduce. If a beat's
work is done by an entrance, the beat is usually a slide. `build.py` prints a motion check
before rendering and names any scene where entrances outnumber motion by more than two to one.

`clear_stage()` is for a genuine change of subject. Within one subject, keep the stage and
transform it (`FadeTransform(old_picture, new_picture)` when the shapes don't match).

## Palette (in explainer_lib)

| name | hex | use |
|---|---|---|
| BG | #1C1C1C | background |
| BLUE | #58C4DD | public values, definitions, theorems |
| YEL | #FFFF00 | the thing to watch, secrets, results being built |
| GRN | #83C167 | correct / easy / fixed / verified |
| RED | #FC6255 | attacker, hard, broken, warnings, a factor being applied |
| GREY | #8A8A8A | captions, scaffolding, headers |
| INK | #ECECEC | body text and maths |

Colour by meaning, and keep each symbol's colour for the whole video: if `m` is yellow in
scene 2 it is yellow in the formula, the HUD and the closing beat. Put the mapping in a comment at the
top of `scenes.py`.

Text font is Inter (`T()`), digit walls use DejaVu Sans Mono (`Mono()`), and maths uses
MathTex (`M()`).

## Layout

- The frame is 14.2 x 8 units. Keep content inside x ±6.6, y +3.2 to -3.6. The header
  (`show_header`) is pinned to the top-left of whatever the camera shows.
- Titles go at `to_edge(UP, buff=1.0-1.2)` so they clear the header. Diagrams sit around y = 0.
- Live readouts (a value that changes during the scene) get a fixed spot away from the moving
  parts. Moving objects pass through empty space, not through labels.
- Closing beat, not a recap card. Bring back the one object that carries the idea (the
  shrinking total, the transformed grid) and the rule it obeys, and move it once more while the
  narration says the point again more sharply.

## Motion and timing

- Camera: `ExplainerScene` is a `MovingCameraScene`. `self.frame` is the camera.
  `self.play(self.focus(mob))` pushes in, `self.play(self.home())` returns. Combine camera
  moves with other animations in one `play`. `self.pin(mob)` keeps a HUD element fixed on
  screen while the camera moves.
- Trackers: drive the picture from as few `ValueTracker`s as possible and compute every
  height, position and label from them in `always_redraw`. Then one `tracker.animate` moves
  everything consistently, and the numbers on screen are always the true values.
  Before `clear_stage` or the end of a scene, `clear_updaters()` on anything left running.
- Run times: 1-2 s for small moves, 2-4 s for a transform the viewer must follow, longer for a
  tracker sweep. Use `b.frac(...)` so these scale with the narration.
- Rate functions: `smooth` (default) for moves, `linear` for sweeps and clocks, `there_and_back`
  for "show a change then undo it", `rush_into` for something about to break.
- `lag_ratio`: 0.1 for a wave, 0.25-0.5 for one-by-one reading, 0.01-0.05 for a ripple across
  a large grid.
- Several things in one `play`, each at its own moment: `during(anim, start, end, total)`.
- Emphasis: `flash_around(mob)` (a light that runs round once), `box_then_fade(mob)`,
  `Circumscribe`, `Indicate` sparingly. Avoid leaving boxes on screen.
- Labels over busy graphics: `backstroke(label)` gives a dark outline.
- Equations: split `MathTex` into the pieces you want to move. Manim CE 0.22 can split
  anywhere, even inside `\frac{` / `}{` / `}` or a superscript (`r"e^{x_i"`, `"- m"`, `"}"`),
  and `TransformMatchingTex` pairs pieces by their exact text. When pieces don't line up,
  `TransformMatchingShapes` matches by glyph shape.

## Overlap fixes that recur

- A label on a moving object: attach it with an updater (`next_to(obj, UP)`), don't place it
  once.
- A readout near a growing curve: put it on the side the curve leaves empty (the low-x side for
  an exponential).
- A limit line with a label: put the label above the line, readouts below.
- A stamp or label on top of a formula: use `next_to(..., DOWN, buff=0.8)`, not `move_to`.
- A row that runs off the right edge: shift the group left, shorten arrows, drop size by 4-6.
- When zooming in on something, include the readouts that change during the zoom in the focus
  target (`self.focus(VGroup(thing, readout))`).
- A diagonal arrow through a box: move the boxes to a separate row so the arrows run between rows.
