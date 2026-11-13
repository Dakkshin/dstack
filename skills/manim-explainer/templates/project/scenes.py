"""Scenes for the starter project. One ExplainerScene per entry in narration.SCENES.

Every number on screen comes from N, which explainer_lib loads from numbers.json.
"""

import os
import sys

sys.path.insert(0, os.environ.get("EXPLAINER_LIB") or "<paste $MK here>/scripts")
from explainer_lib import *  # noqa: E402,F401,F403


class S01_Hook(ExplainerScene):
    def construct(self):
        with self.beat("h1") as b:
            q = T("The one question\nthis video answers", 48, line_spacing=1.2)
            self.play(Write(q), run_time=b.frac(0.6))
        with self.beat("h2") as b:
            self.play(q.animate.scale(0.55).to_edge(UP, buff=0.5), run_time=0.8)
            people = VGroup(*[person(str(i + 1), BLUE, 0.7) for i in range(N["n"])])
            people.arrange(RIGHT, buff=0.5).move_to(DOWN * 0.5)
            self.play(LaggedStart(*[FadeIn(p, shift=0.3 * UP) for p in people], lag_ratio=0.15),
                      run_time=b.frac(0.5))
        self.clear_stage()


class S02_Idea(ExplainerScene):
    def construct(self):
        with self.beat("i1") as b:
            eq = M(f"{N['n']}", r"\times", f"{N['n'] - 1}", r"\div 2")
            self.play(Write(eq), run_time=b.frac(0.4))
        with self.beat("i2") as b:
            result = M("=", fmt(N["pairs"]), color=YEL).next_to(eq, RIGHT, buff=0.3)
            self.play(FadeIn(result, shift=0.2 * LEFT), run_time=b.frac(0.3))
            self.play(Indicate(result, color=YEL), run_time=b.frac(0.2))
        self.clear_stage()


SCENE_ORDER = ["S01_Hook", "S02_Idea"]
