"""Shared engine for narrated Manim explainers.

A project scene file does:

    import sys, os; sys.path.insert(0, os.environ["EXPLAINER_LIB"])
    from explainer_lib import *

and subclasses ExplainerScene. Manim is run with cwd = the project dir, so numbers.json
and durations.json are read from there.

Beat sync: `with self.beat("id") as b:` runs the animations for one narration clip and then
waits until the clip (plus PAD) has played. The real start time of every beat is logged to
timings/<Scene>.json, and build.py places each clip at that time, so audio cannot drift even
when an animation runs longer than its clip.
"""

import json
import os
import subprocess
from pathlib import Path

from manim import *  # noqa: F401,F403

PROJECT = Path.cwd()
N = json.loads((PROJECT / "numbers.json").read_text()) if (PROJECT / "numbers.json").exists() else {}
DUR = json.loads((PROJECT / "durations.json").read_text())["beats"] \
    if (PROJECT / "durations.json").exists() else {}

# 3Blue1Brown palette
BG = "#1C1C1C"
BLUE = "#58C4DD"
YEL = "#FFFF00"
GRN = "#83C167"
RED = "#FC6255"
GREY = "#8A8A8A"
INK = "#ECECEC"
FONT = "Inter"
MONO = "DejaVu Sans Mono"
PAD = 0.85  # breathing room after each clip, seconds

config.background_color = BG
# parallel renders must not share a LaTeX cache: concurrent writes of the same formula corrupt it
if os.environ.get("EXPLAINER_TEX_DIR"):
    config.tex_dir = os.environ["EXPLAINER_TEX_DIR"]


def _has_tex_file(name):
    r = subprocess.run(["kpsewhich", name], capture_output=True, text=True)
    return bool(r.stdout.strip())


# Manim's default template needs standalone.cls (texlive-latexextra). Fall back to article
# with a very wide text block so nothing wraps; dvisvgm crops each formula to its bounds.
if not _has_tex_file("standalone.cls"):
    config.tex_template = TexTemplate(
        documentclass=r"\documentclass[12pt]{article}",
        preamble=r"\usepackage[english]{babel}\usepackage{amsmath}\usepackage{amssymb}"
                 r"\pagestyle{empty}\setlength{\textwidth}{40cm}\setlength{\hsize}{40cm}",
    )


# ---------- text helpers ----------

def T(s, size=36, color=INK, **kw):
    return Text(s, font=FONT, font_size=size, color=color, **kw)


def Mono(s, size=28, color=INK, **kw):
    return Text(s, font=MONO, font_size=size, color=color, **kw)


def M(*s, size=52, color=INK, **kw):
    return MathTex(*s, font_size=size, color=color, **kw)


def fmt(x):
    """Thousands separators that render correctly inside MathTex."""
    return f"{int(x):,}".replace(",", "{,}")


def card(content, color, buff=0.35):
    r = SurroundingRectangle(content, color=color, buff=buff, corner_radius=0.15, stroke_width=3)
    return VGroup(r, content)


# ---------- beat sync ----------

class Beat:
    def __init__(self, scene, bid):
        self.s, self.bid = scene, bid
        self.dur = DUR[bid]

    def frac(self, f, lo=0.4):
        """A run_time that is fraction f of this beat's narration, never below lo."""
        return max(lo, f * self.dur)

    def __enter__(self):
        self.t0 = self.s.renderer.time
        self.s.timings[self.bid] = self.t0
        return self

    def __exit__(self, exc_type, *_):
        if exc_type:
            return False
        rem = self.dur + PAD - (self.s.renderer.time - self.t0)
        if rem > 1 / 30:
            self.s.wait(rem)
        return False


class ExplainerScene(Scene):
    HEADER = ""

    def setup(self):
        self.timings = {}
        self.head = None

    def beat(self, bid):
        return Beat(self, bid)

    def tear_down(self):
        out = PROJECT / "timings"
        out.mkdir(exist_ok=True)
        (out / f"{type(self).__name__}.json").write_text(
            json.dumps({"beats": self.timings, "total": self.renderer.time}, indent=2)
        )

    def show_header(self):
        if self.HEADER:
            self.head = T(self.HEADER, 24, GREY).to_corner(UL, buff=0.45)
            self.play(FadeIn(self.head, shift=0.2 * DOWN), run_time=0.5)

    def clear_stage(self, rt=0.6, keep=()):
        keep = set(keep) | ({self.head} if self.head else set())
        gone = [m for m in self.mobjects if m not in keep]
        if gone:
            self.play(*[FadeOut(m) for m in gone], run_time=rt)


# ---------- simple icons ----------

def padlock(color=BLUE, closed=False, s=1.0):
    body = RoundedRectangle(width=1.0, height=0.8, corner_radius=0.12,
                            fill_color=color, fill_opacity=1, stroke_width=0)
    shackle = Arc(radius=0.3, start_angle=0, angle=PI, color=color, stroke_width=10)
    legs = VGroup(Line(ORIGIN, 0.25 * DOWN), Line(ORIGIN, 0.25 * DOWN)).set_stroke(color, 10)
    legs[0].move_to(shackle.get_start() + 0.12 * DOWN)
    legs[1].move_to(shackle.get_end() + 0.12 * DOWN)
    sh = VGroup(shackle, legs)
    sh.next_to(body, UP, buff=-0.12)
    if not closed:
        sh.shift(0.28 * UP)
    hole = VGroup(Circle(0.07, fill_color=BG, fill_opacity=1, stroke_width=0),
                  Triangle(fill_color=BG, fill_opacity=1, stroke_width=0).scale(0.08).rotate(PI)
                  .shift(0.09 * DOWN)).move_to(body).shift(0.04 * UP)
    return VGroup(body, sh, hole).scale(s)


def key_icon(color=YEL, s=1.0):
    ring = Circle(0.22, color=color, stroke_width=8)
    shaft = Line(ring.get_right(), ring.get_right() + 0.8 * RIGHT, color=color, stroke_width=8)
    t1 = Line(shaft.get_end(), shaft.get_end() + 0.2 * DOWN, color=color, stroke_width=8)
    t2 = Line(shaft.get_end() + 0.22 * LEFT, shaft.get_end() + 0.22 * LEFT + 0.15 * DOWN,
              color=color, stroke_width=8)
    return VGroup(ring, shaft, t1, t2).scale(s)


def person(name, color, s=1.0):
    head = Circle(0.24, fill_color=color, fill_opacity=1, stroke_width=0)
    body = Arc(radius=0.42, start_angle=0, angle=PI, fill_color=color, fill_opacity=1,
               stroke_width=0).next_to(head, DOWN, buff=0.06)
    label = T(name, 26, color).next_to(body, DOWN, buff=0.15)
    return VGroup(head, body, label).scale(s)


def box_icon(w=1.8, h=1.2):
    b = Rectangle(width=w, height=h, fill_color="#2E2A24", fill_opacity=1, color="#B8A07A",
                  stroke_width=4)
    lid = Line(b.get_corner(UL) + 0.3 * DOWN, b.get_corner(UR) + 0.3 * DOWN, color="#B8A07A",
               stroke_width=4)
    return VGroup(b, lid)
