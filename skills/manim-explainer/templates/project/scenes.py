"""Scenes for the starter project. One ExplainerScene per entry in narration.SCENES.

Every number on screen comes from N, which explainer_lib loads from numbers.json.
The starter shows the house style (references/style.md): the picture stays on screen and
changes. A tracker drives a live count, a camera move frames the detail, and the equation is
built from copies of what is already there.
"""

import os
import sys
from itertools import combinations

sys.path.insert(0, os.environ.get("EXPLAINER_LIB") or "<paste $MK here>/scripts")
from explainer_lib import *  # noqa: E402,F401,F403


def room():
    """The same circle of people in every scene, so a cut between scenes keeps the picture."""
    people = VGroup(*[person(str(i + 1), BLUE, 0.55) for i in range(N["n"])])
    for i, p in enumerate(people):
        p.move_to(2.2 * np.array([np.cos(TAU * i / N["n"] + PI / 2),
                                  np.sin(TAU * i / N["n"] + PI / 2), 0]) + DOWN * 0.4)
    return people


class S01_Hook(ExplainerScene):
    def construct(self):
        with self.beat("h1") as b:
            q = T("How many handshakes?", 52)
            self.play(Write(q), run_time=b.frac(0.5))
        with self.beat("h2") as b:
            people = room()
            self.play(q.animate.scale(0.6).to_edge(UP, buff=0.5),
                      LaggedStart(*[FadeIn(p, scale=0.6) for p in people], lag_ratio=0.12),
                      run_time=b.frac(0.5))


class S02_Idea(ExplainerScene):
    def construct(self):
        people = room()
        self.add(people)
        pairs = list(combinations(range(N["n"]), 2))
        lines = VGroup(*[Line(people[a][0].get_center(), people[c][0].get_center(),
                              color=YEL, stroke_width=3) for a, c in pairs])
        shown = ValueTracker(0)
        count = always_redraw(lambda: VGroup(T("handshakes", 30, GREY),
                                             Mono(str(int(shown.get_value())), 40, YEL))
                              .arrange(RIGHT, buff=0.3).to_corner(UR, buff=0.6))

        with self.beat("i1") as b:
            # one person's hands first, with the camera in close
            mine = VGroup(*[l for l, (a, _) in zip(lines, pairs) if a == 0])
            self.play(self.focus(VGroup(people[0], *[people[i] for i in range(1, N["n"])][:2]),
                                 width=9), run_time=b.frac(0.2))
            self.play(LaggedStart(*[Create(l) for l in mine], lag_ratio=0.2),
                      run_time=b.frac(0.3))
            self.play(self.home(), run_time=b.frac(0.2))

        with self.beat("i2") as b:
            shown.set_value(len(mine))
            self.add(count)
            self.play(LaggedStart(*[Create(l) for l in lines[len(mine):]], lag_ratio=0.1),
                      shown.animate.set_value(len(pairs)), run_time=b.frac(0.4), rate_func=linear)
            eq = M(f"{N['n']}", r"\times", f"{N['n'] - 1}", r"\div 2", "=", fmt(N["pairs"]))
            eq.to_edge(DOWN, buff=0.4)
            eq[-1].set_color(YEL)
            self.play(*dim(people, lines, to=0.35), Write(eq[:-1]), run_time=b.frac(0.2))
            self.play(TransformFromCopy(count[1], eq[-1], path_arc=-PI / 3), run_time=b.frac(0.2))
        count.clear_updaters()


SCENE_ORDER = ["S01_Hook", "S02_Idea"]
