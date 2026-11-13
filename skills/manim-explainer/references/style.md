# Style reference

## Palette (in explainer_lib)

| name | hex | use |
|---|---|---|
| BG | #1C1C1C | background |
| BLUE | #58C4DD | public values, definitions, theorems |
| YEL | #FFFF00 | the thing to watch, secrets, results being built |
| GRN | #83C167 | correct / easy / fixed / verified |
| RED | #FC6255 | attacker, hard, broken, warnings |
| GREY | #8A8A8A | captions, scaffolding, headers |
| INK | #ECECEC | body text and maths |

Text font is Inter (`T()`), digit walls use DejaVu Sans Mono (`Mono()`), and maths uses MathTex (`M()`).

## Layout

- The frame is 14.2 x 8 units. Keep content inside x ±6.6, y +3.2 to -3.6. The header
  (`show_header`) sits at the top-left corner.
- One idea on screen. Call `self.clear_stage()` between ideas, which keeps the header.
- Titles go at `to_edge(UP, buff=1.0-1.2)` so they clear the header. Diagrams sit around y = 0.
- A sidebar of accumulated results (like the RSA key-gen rail) is fine. Keep it under 0.65 scale.
- Recap cards: one numbered row per point, `Tex` at font_size 40+, longest row under 12 units.
  Shorten the text rather than shrink the font.

## Animation conventions

- Equation evolution: `TransformMatchingTex` between successive forms in the same position.
- Emphasis: `Circumscribe`, `Indicate`, colour change. Use `Flash` sparingly.
- Fade-ins can carry a small `shift` (0.15-0.3) for direction. Use `Write` for maths.
- Values that change over time: `ValueTracker` + `always_redraw`. For a final state, swap in a
  static mobject so colour and number are exact.

## Overlap fixes that recur

- Stamp or label on top of a formula: use `next_to(..., DOWN, buff=0.8)`, not `move_to`.
- Result next to a dial or diagram: give it its own column (x around -3.2), not `next_to(formula)`.
- A row that runs off the right edge: shift the group left, shorten arrows, drop size by 4-6.
- A strike-through label: group the text with its strike line before `arrange`, otherwise the
  line takes up a slot and pushes neighbours away.
- A diagonal arrow through a box: move the boxes to a separate row so the arrows run between rows.
