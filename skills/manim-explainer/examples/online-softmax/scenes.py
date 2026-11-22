"""Online softmax: one pass instead of two. Every number on screen comes from N (numbers.json).

Colour by meaning, kept across scenes: scores BLUE, the max m YELLOW, the running total d
GREEN, the rescale factor RED.
"""

import math
import os
import sys

sys.path.insert(0, os.environ.get("EXPLAINER_LIB") or
                os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "scripts"))
from explainer_lib import *  # noqa: E402,F401,F403

X = N["x"]
E = [math.exp(v) for v in X]
SAFE = N["safe"]
TEXC = {"m": YEL, "d": GRN}


def cells(values, step=1.05, side=0.8, size=30, x0=None, y=0.0, color=INK):
    """A row of memory cells holding values."""
    x0 = -(len(values) - 1) * step / 2 if x0 is None else x0
    g = VGroup()
    for i, v in enumerate(values):
        sq = Square(side, color=GREY, stroke_width=2).move_to([x0 + i * step, y, 0])
        g.add(VGroup(sq, Mono(str(v), size, color).move_to(sq)))
    return g


# ---------------------------------------------------------------------------------------------
class S01_Softmax(ExplainerScene):
    HEADER = "What softmax does"

    def construct(self):
        self.show_header()
        base_y, u_raw, top = -2.4, 0.42, 3.4
        xs = [-4.5 + i * 1.5 for i in range(6)]
        stage = ValueTracker(0.0)  # 0 = raw scores, 1 = exponentials

        def heights():
            t = stage.get_value()
            return [(1 - t) * X[i] * u_raw + t * E[i] / max(E) * top for i in range(6)]

        def draw():
            g = VGroup()
            for i, h in enumerate(heights()):
                c = interpolate_color(ManimColor(BLUE), ManimColor(YEL), stage.get_value()
                                      if X[i] == max(X) else 0)
                g.add(Rectangle(width=0.8, height=max(h, 1e-3), stroke_width=0, fill_color=c,
                                fill_opacity=0.9).move_to([xs[i], base_y + h / 2, 0]))
            return g

        bars = always_redraw(draw)
        floor = Line([-5.4, base_y, 0], [3.9, base_y, 0], color=GREY, stroke_width=2)

        def top_labels(texts, color=INK):
            g = VGroup(*[Mono(t, 24, color) for t in texts])
            for i, lab in enumerate(g):
                lab.add_updater(lambda m, i=i: m.next_to(bars[i], UP, buff=0.12))
            return g

        raw = top_labels([str(v) for v in X])

        with self.beat("a1") as b:
            self.play(Create(floor), run_time=0.6)
            self.add(bars)
            grow = ValueTracker(0.0)
            bars.clear_updaters()
            bars.add_updater(lambda m: m.become(draw().stretch(max(grow.get_value(), 1e-3), 1,
                                                               about_edge=DOWN)))
            self.play(grow.animate.set_value(1), run_time=b.frac(0.35), rate_func=smooth)
            bars.clear_updaters()
            bars.add_updater(lambda m: m.become(draw()))
            self.play(LaggedStart(*[FadeIn(l, shift=0.2 * UP) for l in raw], lag_ratio=0.1),
                      run_time=b.frac(0.25))

        formula = M(r"\frac{", r"e^{x_i}", r"}{", r"\sum_j e^{x_j}", r"}", size=56)
        formula.move_to([0.6, 2.3, 0])
        name = T("softmax", 32, GREY).next_to(formula, LEFT, buff=0.5)
        with self.beat("a2") as b:
            self.play(Write(formula), FadeIn(name, shift=0.2 * RIGHT), run_time=b.frac(0.35))

        with self.beat("a3") as b:
            self.play(flash_around(formula[1], color=YEL), run_time=b.frac(0.2))
            exps = top_labels([f"{e:,.0f}" if e >= 10 else f"{e:.1f}" for e in E])
            for l in exps:
                l.update()
            self.play(stage.animate.set_value(1),
                      *[FadeTransform(raw[i], exps[i]) for i in range(6)],
                      run_time=b.frac(0.55), rate_func=smooth)

        # the total: every bar stacks into one column; that column is "1"
        col_x = 5.6
        with self.beat("a4") as b:
            self.play(flash_around(formula[3], color=GRN), run_time=b.frac(0.15))
            hs = heights()
            segs, y = VGroup(), base_y
            for i, h in enumerate(hs):
                segs.add(Rectangle(width=0.8, height=h, stroke_color=BG, stroke_width=2,
                                   fill_color=bars[i].get_fill_color(), fill_opacity=0.9)
                         .move_to([col_x, y + h / 2, 0]))
                y += h
            self.play(LaggedStart(*[TransformFromCopy(bars[i], segs[i], path_arc=-PI / 4)
                                    for i in range(6)], lag_ratio=0.12),
                      run_time=b.frac(0.3))
            one = M("1", color=GRN, size=48).next_to(segs, UP, buff=0.2)
            pcts = top_labels([f"{v}%" for v in N["pct"]], INK)
            for l in pcts:
                l.update()
            self.play(FadeIn(one, shift=0.2 * DOWN),
                      *[FadeTransform(exps[i], pcts[i]) for i in range(6)],
                      run_time=b.frac(0.2))
            self.play(Circumscribe(VGroup(bars[4], pcts[4]), color=YEL), run_time=b.frac(0.15))
        for l in pcts:
            l.clear_updaters()
        bars.clear_updaters()


# ---------------------------------------------------------------------------------------------
class S02_Overflow(ExplainerScene):
    HEADER = "Why we subtract the max"

    def construct(self):
        self.show_header()
        xt, yt = ValueTracker(0.0), ValueTracker(3000.0)
        LIM = N["fp16_max"]

        def ax():
            return Axes(x_range=[0, 13, 1], y_range=[0, yt.get_value(), yt.get_value() / 4],
                        x_length=10, y_length=5.0,
                        axis_config={"color": GREY, "stroke_width": 2, "include_tip": False}
                        ).move_to([-0.6, -0.5, 0])

        def draw():
            a = ax()
            cap = math.log(yt.get_value() * 1.02)
            x = min(xt.get_value(), cap)
            g = VGroup(a)
            if x > 0.02:
                g.add(a.plot(math.exp, x_range=[0, x], color=YEL, stroke_width=5))
            g.add(Dot(a.c2p(x, math.exp(x)), radius=0.09, color=YEL))
            return g

        a0 = ax()
        xnums = VGroup(*[Mono(str(k), 20, GREY).next_to(a0.c2p(k, 0), DOWN, buff=0.15)
                         for k in range(0, 13, 2)])
        plot = always_redraw(draw)

        def readout():
            x = xt.get_value()
            if x > N["ln16"]:
                return VGroup(M(r"e^{x}", "=", r"\infty", color=RED, size=44)).move_to([-3.0, 0.9, 0])
            return VGroup(M(r"e^{x}", "=", size=44),
                          Mono(f"{math.exp(x):,.0f}", 32, YEL)).arrange(RIGHT, buff=0.25)\
                .move_to([-3.0, 0.9, 0])

        xlab = always_redraw(lambda: M(f"x = {xt.get_value():.1f}", size=36, color=BLUE)
                             .move_to([-3.0, 0.2, 0]))
        ro = always_redraw(readout)

        with self.beat("b1") as b:
            self.play(FadeIn(plot), FadeIn(xnums), FadeIn(ro), FadeIn(xlab), run_time=0.6)
            self.play(xt.animate.set_value(8), run_time=b.frac(0.75), rate_func=linear)

        with self.beat("b2") as b:
            # the y axis has to keep stretching to hold the curve
            self.play(yt.animate.set_value(72000), xt.animate.set_value(11.0),
                      run_time=b.frac(0.35), rate_func=smooth)
            a = ax()
            limit = DashedLine(a.c2p(0, LIM), a.c2p(13, LIM), color=RED, stroke_width=3)
            lim_lab = T(f"{LIM:,}  largest half-precision number", 22, RED)\
                .next_to(limit, UP, buff=0.12).align_to(limit, LEFT).shift(0.3 * RIGHT)
            self.play(Create(limit), FadeIn(lim_lab, shift=0.1 * UP), run_time=b.frac(0.15))
            self.play(xt.animate.set_value(12), run_time=b.frac(0.2), rate_func=rush_into)
            self.play(Flash(plot[-1].get_center(), color=RED, line_length=0.4), run_time=0.6)

        # same scores, now on a number line, slid down by the max
        shift = ValueTracker(0.0)
        line = NumberLine(x_range=[-8, 8, 1], length=13, color=GREY, include_numbers=True,
                          font_size=24).move_to([0, -1.4, 0])
        top = max(X)

        def dots():
            g = VGroup()
            for v in X:
                p = line.n2p(v - shift.get_value())
                c = YEL if v == top else BLUE
                g.add(VGroup(Dot(p, radius=0.11, color=c),
                             Mono(f"{v - shift.get_value():.0f}", 24, c).next_to(p, UP, buff=0.35)))
            return g

        pts = always_redraw(dots)
        with self.beat("b3") as b:
            self.play(FadeOut(ro), FadeOut(xlab), FadeOut(limit), FadeOut(lim_lab), run_time=0.4)
            plot.clear_updaters()
            self.play(FadeTransform(VGroup(plot, xnums), line), FadeIn(pts), run_time=b.frac(0.15))
            self.play(Indicate(pts[4], color=YEL), run_time=0.8)
            self.play(shift.animate.set_value(top), run_time=b.frac(0.35), rate_func=smooth)
            zero = DashedLine(line.n2p(0) + 0.1 * DOWN, line.n2p(0) + 1.6 * UP, color=GRN)
            neg = Brace(Line(line.n2p(-8), line.n2p(0)), DOWN, color=BLUE, buff=0.55)
            neg_lab = M(r"e^{\text{negative}} < 1", size=34, color=BLUE).next_to(neg, DOWN, 0.1)
            self.play(Create(zero), GrowFromCenter(neg), FadeIn(neg_lab, shift=0.15 * UP),
                      run_time=b.frac(0.2))

        f1 = M(r"\frac{", r"e^{x_i}", r"}{", r"\sum_j e^{x_j}", r"}", size=52).move_to([0, 2.2, 0])
        f2 = M(r"\frac{", r"e^{x_i}", r"e^{-m}", r"}{", r"\sum_j e^{x_j}", r"e^{-m}", r"}",
               size=52).move_to(f1)
        f2[2].set_color(YEL), f2[5].set_color(YEL)
        f3 = M(r"\frac{", r"e^{x_i - m}", r"}{", r"\sum_j e^{x_j - m}", r"}",
               size=52).move_to(f1)
        with self.beat("b4") as b:
            self.play(Write(f1), run_time=b.frac(0.15))
            self.play(TransformMatchingTex(f1, f2), run_time=b.frac(0.2))
            self.play(flash_around(f2[2], YEL, rt=0.8), flash_around(f2[5], YEL, rt=0.8))
            self.play(TransformMatchingShapes(f2, f3), run_time=b.frac(0.2))
        self.clear_stage()


# ---------------------------------------------------------------------------------------------
class S03_Passes(ExplainerScene):
    HEADER = "The price: an extra pass"

    def construct(self):
        self.show_header()
        step = 1.05
        row = cells(X, step=step, y=0.9)
        x0 = row[0].get_x()
        more = VGroup(*[Square(0.8, color=GREY, stroke_width=2, stroke_opacity=0.5)
                        .move_to([x0 + (6 + k) * step, 0.9, 0]) for k in range(60)])
        mem = T("memory: big but slow", 24, GREY).next_to(row, UP, buff=0.35).align_to(row, LEFT)

        with self.beat("c1") as b:
            self.play(LaggedStart(*[FadeIn(c, shift=0.2 * DOWN) for c in row], lag_ratio=0.1),
                      FadeIn(mem), run_time=b.frac(0.25))
            self.add(more)
            self.play(self.frame.animate.set(width=48).move_to([22, 0.9, 0]),
                      run_time=b.frac(0.35))
            self.play(self.home(), run_time=b.frac(0.2))
            self.remove(more)

        cur = ValueTracker(0.0)
        cursor = always_redraw(lambda: SurroundingRectangle(
            row[0], color=YEL, buff=0.08, stroke_width=5).move_to(
            [x0 + cur.get_value() * step, 0.9, 0]))
        seen = lambda: int(min(5, math.floor(cur.get_value() + 1e-6))) + 1

        def tally(i, text, color):
            r = RoundedRectangle(width=3.4, height=0.7, corner_radius=0.12, stroke_color=color,
                                 fill_color=color, fill_opacity=0.15)
            return VGroup(r, T(text, 24, color).move_to(r)).move_to([-4 + i * 4, -2.7, 0])

        m_read = always_redraw(lambda: VGroup(
            M("m", "=", size=40, color=YEL), Mono(str(max(X[:seen()])), 32, YEL)
        ).arrange(RIGHT, buff=0.25).move_to([-3.2, -1.0, 0]))
        d_read = always_redraw(lambda: VGroup(
            M("d", "=", size=40, color=GRN), Mono(f"{sum(SAFE[:seen()]):.2f}", 32, GRN)
        ).arrange(RIGHT, buff=0.25).move_to([0.5, -1.0, 0]))
        t1, t2, t3 = tally(0, "pass 1: max", YEL), tally(1, "pass 2: sum", GRN), \
            tally(2, "pass 3: divide", BLUE)

        with self.beat("c2") as b:
            self.add(cursor)
            self.play(FadeIn(m_read), GrowFromEdge(t1, LEFT), run_time=0.5)
            self.play(cur.animate.set_value(5), run_time=b.frac(0.6), rate_func=linear)

        with self.beat("c3") as b:
            self.play(cur.animate.set_value(0), run_time=0.5)
            self.play(FadeIn(d_read), GrowFromEdge(t2, LEFT), run_time=0.4)
            self.play(cur.animate.set_value(5), run_time=b.frac(0.6), rate_func=linear)

        with self.beat("c4") as b:
            self.play(cur.animate.set_value(0), GrowFromEdge(t3, LEFT), run_time=0.5)
            sweep = b.frac(0.25)
            probs = [Mono(f"{p:.3f}", 19, BLUE).move_to(row[i]) for i, p in enumerate(N["p"])]
            self.play(cur.animate.set_value(5),
                      LaggedStart(*[Transform(row[i][1], probs[i]) for i in range(6)],
                                  lag_ratio=1.0),
                      run_time=sweep, rate_func=linear)
            self.play(FadeOut(cursor), FadeOut(m_read), FadeOut(d_read), *dim(t3, row, to=0.3),
                      run_time=0.5)
            # can passes 1 and 2 collapse into one?
            q = M("?", size=72, color=RED).move_to([-2, -1.95, 0])
            self.play(t1.animate.shift(0.28 * RIGHT), t2.animate.shift(0.28 * LEFT),
                      FadeIn(q, scale=1.5), run_time=b.frac(0.15))
            need = T("need the max before adding,\nbut the max needs every score",
                     26, RED, line_spacing=1.1).move_to([1.6, -0.9, 0])
            self.play(FadeIn(need, shift=0.2 * UP), run_time=b.frac(0.1))
            self.play(Wiggle(q), run_time=1.0)
        self.clear_stage()


# ---------------------------------------------------------------------------------------------
class S04_Online(ExplainerScene):
    HEADER = "Fix the sum as you go"
    U = 3.0          # height of e^0
    BASE = -2.8

    def construct(self):
        self.show_header()
        U, BASE = self.U, self.BASE
        xs = [-5.0 + i * 1.0 for i in range(6)]
        row = VGroup(*[VGroup(Square(0.72, color=GREY, stroke_width=2),
                              Mono(str(v), 28)).move_to([xs[i], 2.45, 0])
                       for i, v in enumerate(X)])
        for c in row:
            c[1].move_to(c[0])
        mt, nt = ValueTracker(X[0]), ValueTracker(0.0)
        col_x = 2.6

        def hs():
            n, m = nt.get_value(), mt.get_value()
            out = []
            for i in range(6):
                f = min(max(n - i, 0.0), 1.0)
                out.append(f * math.exp(X[i] - m) * U)
            return out

        def colour(i):
            return YEL if X[i] == max(X[:max(1, math.ceil(nt.get_value() - 1e-6))]) else BLUE

        def draw_bars():
            g = VGroup()
            for i, h in enumerate(hs()):
                g.add(Rectangle(width=0.6, height=max(h, 1e-3), stroke_width=0,
                                fill_color=colour(i), fill_opacity=0.9 if h > 1e-3 else 0)
                      .move_to([xs[i], BASE + h / 2, 0]))
            return g

        def draw_stack():
            g, y = VGroup(), BASE
            for i, h in enumerate(hs()):
                g.add(Rectangle(width=0.9, height=max(h, 1e-3), stroke_color=BG,
                                stroke_width=2 if h > 1e-3 else 0,
                                fill_color=colour(i), fill_opacity=0.9 if h > 1e-3 else 0)
                      .move_to([col_x, y + h / 2, 0]))
                y += h
            return g

        bars, stack = always_redraw(draw_bars), always_redraw(draw_stack)
        floor = Line([-5.6, BASE, 0], [3.3, BASE, 0], color=GREY, stroke_width=2)
        ruler = DashedLine([-5.6, BASE + U, 0], [0.4, BASE + U, 0], color=GREY, stroke_width=2)
        ruler_lab = M(r"e^{0} = 1", size=28, color=GREY).next_to(ruler, RIGHT, buff=0.15)
        d_lab = M("d", size=40, color=GRN).next_to([col_x, BASE, 0], DOWN, buff=0.15)

        hud = VGroup(
            VGroup(M("m", "=", size=44, color=YEL),
                   live_number(lambda: mt.get_value(), places=0, size=40, color=YEL)),
            VGroup(M("d", "=", size=44, color=GRN),
                   live_number(lambda: sum(hs()) / U, places=2, size=40, color=GRN)),
        )
        for i, line in enumerate(hud):
            line[0].move_to([4.1, 1.5 - i * 0.8, 0])
            line[1].clear_updaters()
            line[1].next_to(line[0], RIGHT, buff=0.25)
        hud[0][1].add_updater(lambda m: m.set_value(mt.get_value()))
        hud[1][1].add_updater(lambda m: m.set_value(sum(hs()) / U))

        cursor = SurroundingRectangle(row[0], color=YEL, buff=0.07, stroke_width=5)

        with self.beat("d1") as b:
            self.play(LaggedStart(*[FadeIn(c, shift=0.2 * DOWN) for c in row], lag_ratio=0.08),
                      Create(floor), run_time=b.frac(0.2))
            self.add(bars, stack)
            self.play(FadeIn(hud[0], shift=0.2 * LEFT), run_time=b.frac(0.15))
            self.play(FadeIn(hud[1], shift=0.2 * LEFT), FadeIn(d_lab), run_time=b.frac(0.15))
            self.play(Create(ruler), FadeIn(ruler_lab), run_time=b.frac(0.15))

        def take(i, b, frac_grow=0.25):
            self.play(cursor.animate.move_to(row[i]), run_time=0.5)
            self.play(nt.animate.set_value(i + 1), run_time=b.frac(frac_grow))

        def rescale(i, b, frac=0.3, zoom=True):
            old, new = mt.get_value(), X[i]
            k = M(r"\times\, e^{", f"{old:.0f}", "-", f"{new}", "}", size=40, color=RED)
            k.next_to([col_x - 0.6, BASE + sum(hs()) * 0.5, 0], LEFT, buff=0.1)
            k[1].set_color(YEL), k[3].set_color(YEL)
            self.play(cursor.animate.move_to(row[i]), FadeIn(k, shift=0.2 * LEFT), run_time=0.6)
            area = VGroup(stack.copy(), k, hud, Dot([col_x, BASE, 0]))
            if zoom:
                self.play(self.focus(area, pad=1.25), run_time=0.8)
            self.play(mt.animate.set_value(new), run_time=b.frac(frac), rate_func=smooth)
            self.play(FadeOut(k), *( [self.home()] if zoom else []), run_time=0.6)

        with self.beat("d2") as b:
            self.play(Create(cursor), run_time=0.4)
            self.play(nt.animate.set_value(1), run_time=b.frac(0.3))
            self.play(flash_around(hud[1], GRN), run_time=0.8)

        with self.beat("d3") as b:
            take(1, b)
            self.play(Indicate(hud[1][1], color=GRN), run_time=0.8)

        with self.beat("d4") as b:
            rescale(2, b, frac=0.3)
            self.play(nt.animate.set_value(3), run_time=b.frac(0.15))

        with self.beat("d5") as b:
            take(3, b, frac_grow=0.12)
            rescale(4, b, frac=0.2, zoom=False)
            self.play(nt.animate.set_value(5), run_time=b.frac(0.12))

        with self.beat("d6") as b:
            take(5, b, frac_grow=0.2)
            check = VGroup(T("slow way:", 24, GREY), Mono(f"{N['d']:.2f}", 28, GRN))\
                .arrange(RIGHT, buff=0.2).next_to(hud, DOWN, buff=0.5).align_to(hud, LEFT)
            self.play(FadeIn(check, shift=0.2 * UP), run_time=0.6)
            self.play(flash_around(VGroup(hud[1], check), GRN), run_time=1.2)
        for m in (bars, stack, *hud[0], *hud[1]):
            m.clear_updaters()
        self.clear_stage()


# ---------------------------------------------------------------------------------------------
OLD, NEW = r"m_{\text{old}}", r"m_{\text{new}}"


class S05_Why(ExplainerScene):
    HEADER = "Why the shrink is exact"

    def construct(self):
        self.show_header()
        l1 = M("d", "=", r"\sum_i e^{", "x_i", "-", OLD, "}", size=56)
        l2 = M("d", r"\cdot", r"e^{", OLD, "-", NEW, "}", "=", r"\sum_i e^{", "x_i", "-", OLD,
               "}", r"\cdot", r"e^{", OLD, "-", NEW, "}", size=56)
        l3 = M("d", r"\cdot", r"e^{", OLD, "-", NEW, "}", "=", r"\sum_i e^{", "x_i", "-", OLD,
               "+", OLD, "-", NEW, "}", size=56)
        l4 = M("d", r"\cdot", r"e^{", OLD, "-", NEW, "}", "=", r"\sum_i e^{", "x_i", "-", NEW,
               "}", size=56)
        for l in (l1, l2, l3, l4):
            l.move_to(UP * 0.8)
            l.set_color_by_tex("d", GRN)
            for part in l:
                if part.get_tex_string() == OLD:
                    part.set_color(YEL)
                elif part.get_tex_string() == NEW:
                    part.set_color(ORANGE)
        for l in (l2, l3, l4):
            l[1:7].set_color(RED)
            l[3].set_color(YEL), l[5].set_color(ORANGE)

        with self.beat("e1") as b:
            self.play(Write(l1), run_time=b.frac(0.4))
            self.play(Circumscribe(l1[5], color=YEL), run_time=b.frac(0.3))

        with self.beat("e2") as b:
            self.play(TransformMatchingTex(l1, l2, path_arc=PI / 6), run_time=b.frac(0.18))
            self.play(TransformMatchingTex(l2, l3), run_time=b.frac(0.15))
            cancel = l3[10:14]
            strike = Line(cancel.get_corner(DL), cancel.get_corner(UR), color=RED, stroke_width=5)
            self.play(Create(strike), run_time=b.frac(0.1))
            self.play(self.focus(l3[8:], width=8), run_time=b.frac(0.1))
            self.play(FadeOut(strike), TransformMatchingTex(l3, l4), run_time=b.frac(0.15))
            self.play(self.home(), flash_around(l4[8:], ORANGE), run_time=b.frac(0.12))

        alg = VGroup(
            M("m'", "=", r"\max(", "m", ",", "x", ")", size=50),
            M("d'", "=", "d", r"\cdot", r"e^{", "m", "-", "m'", "}", "+", r"e^{", "x", "-", "m'",
              "}", size=50),
        ).arrange(DOWN, buff=0.5, aligned_edge=LEFT).move_to(DOWN * 1.9)
        for part in [*alg[0], *alg[1]]:
            s = part.get_tex_string()
            part.set_color({"m": YEL, "m'": YEL, "d": GRN, "d'": GRN}.get(s, INK))
        alg[1][3:9].set_color(RED), alg[1][5].set_color(YEL), alg[1][7].set_color(YEL)
        box = SurroundingRectangle(alg, color=GREY, buff=0.3, corner_radius=0.15)

        with self.beat("e3") as b:
            self.play(l4.animate.scale(0.75).shift(UP * 1.2), run_time=0.6)
            self.play(Write(alg[0]), run_time=b.frac(0.2))
            self.play(Write(alg[1][:3]), run_time=b.frac(0.1))
            self.play(TransformFromCopy(l4[1:7], alg[1][3:9], path_arc=-PI / 4),
                      run_time=b.frac(0.2))
            self.play(Write(alg[1][9:]), Create(box), run_time=b.frac(0.2))
        self.clear_stage()


# ---------------------------------------------------------------------------------------------
class S06_Merge(ExplainerScene):
    HEADER = "Splitting the work"
    U, BASE = 2.6, -2.6

    def construct(self):
        self.show_header()
        U, BASE = self.U, self.BASE
        H = N["half"]

        strips = VGroup(*[RoundedRectangle(width=9, height=0.6, corner_radius=0.1,
                                           stroke_color=c, fill_color=c, fill_opacity=0.15)
                          for c in (YEL, GRN, BLUE)]).arrange(DOWN, buff=0.25).move_to(UP * 0.3)
        labels = VGroup(*[T(t, 24, c).move_to(s) for t, c, s in
                          zip(("pass 1: max", "pass 2: sum", "pass 3: divide"),
                              (YEL, GRN, BLUE), strips)])
        with self.beat("f1") as b:
            self.play(LaggedStart(*[GrowFromEdge(VGroup(s, l), LEFT)
                                    for s, l in zip(strips, labels)], lag_ratio=0.25),
                      run_time=b.frac(0.35))
            merged = RoundedRectangle(width=9, height=0.6, corner_radius=0.1, stroke_color=YEL,
                                      fill_color=GRN, fill_opacity=0.2).move_to(strips[:2])
            mlab = T("online: max and sum together", 24, GRN).move_to(merged)
            self.play(ReplacementTransform(VGroup(strips[0], strips[1]), merged),
                      ReplacementTransform(VGroup(labels[0], labels[1]), mlab),
                      VGroup(strips[2], labels[2]).animate.next_to(merged, DOWN, buff=0.25),
                      run_time=b.frac(0.35))

        # two workers, two partial (m, d) pairs, one merge
        halves = [X[:3], X[3:]]
        row = cells(X, step=1.0, y=2.2, size=26)
        with self.beat("f2") as b:
            self.play(FadeTransform(VGroup(merged, mlab, strips[2], labels[2]), row),
                      run_time=b.frac(0.15))
            self.play(row[:3].animate.shift(2.0 * LEFT), row[3:].animate.shift(2.0 * RIGHT),
                      run_time=b.frac(0.15))
            stacks = VGroup()
            for k, (half, mk) in enumerate(zip(halves, (H["m1"], H["m2"]))):
                g, y = VGroup(), BASE
                for v in half:
                    h = math.exp(v - mk) * U
                    g.add(Rectangle(width=1.0, height=h, stroke_color=BG, stroke_width=2,
                                    fill_color=YEL if v == mk else BLUE, fill_opacity=0.9)
                          .move_to([0, y + h / 2, 0]))
                    y += h
                g.move_to([(-3.0, 3.0)[k], g.get_center()[1], 0])
                stacks.add(g)
            self.play(LaggedStart(*[TransformFromCopy(row[k * 3:k * 3 + 3], stacks[k])
                                    for k in range(2)], lag_ratio=0.4), run_time=b.frac(0.3))
            tags = VGroup(*[M(f"m={mk}", size=36, color=YEL).next_to(stacks[k], UP, buff=0.25)
                            for k, mk in enumerate((H["m1"], H["m2"]))])
            self.play(LaggedStart(*[FadeIn(t, shift=0.2 * DOWN) for t in tags], lag_ratio=0.4),
                      run_time=b.frac(0.2))

        with self.beat("f3") as b:
            k = M(r"\times\, e^{", f"{H['m1']}", "-", f"{H['m2']}", "}", size=40, color=RED)
            k[1].set_color(YEL), k[3].set_color(YEL)
            k.next_to(stacks[0], LEFT, buff=0.3)
            self.play(FadeIn(k, shift=0.2 * RIGHT), run_time=0.6)
            self.play(stacks[0].animate.stretch(H["scale1"], 1, about_edge=DOWN),
                      tags[0].animate.shift(DOWN * stacks[0].height * (1 - H["scale1"])),
                      run_time=b.frac(0.2))
            self.play(FadeOut(k), FadeOut(tags[0]), run_time=0.4)
            self.play(stacks[0].animate.next_to(stacks[1], UP, buff=0),
                      tags[1].animate.shift(UP * stacks[0].height),
                      run_time=b.frac(0.2))
            total = M("d", "=", f"{H['d']:.2f}", size=44, color=GRN)\
                .next_to(VGroup(stacks), RIGHT, buff=0.6)
            self.play(Write(total), run_time=b.frac(0.1))
            self.play(flash_around(total, GRN), run_time=0.9)

        # FlashAttention: tiles stream across a matrix that is never stored
        grid = VGroup(*[Square(0.42, stroke_color=GREY, stroke_width=1, stroke_opacity=0.6)
                        for _ in range(12 * 12)]).arrange_in_grid(12, 12, buff=0)
        grid.move_to([-2.5, -0.4, 0])
        tile = Square(0.42 * 3, color=YEL, stroke_width=5, fill_color=YEL, fill_opacity=0.25)
        with self.beat("f4") as b:
            self.play(FadeOut(VGroup(row, stacks, tags[1], total)), run_time=0.5)
            self.play(LaggedStart(*[FadeIn(s) for s in grid], lag_ratio=0.004),
                      run_time=b.frac(0.15))
            tile.move_to(grid[0:3].get_center() + DOWN * 0.42).align_to(grid, UL)
            note = T("attention scores:\nnever stored whole", 26, GREY, line_spacing=1.1)\
                .move_to([3.8, 0.8, 0])
            hud = VGroup(M("m,\\ d,\\ \\text{output}", size=38, color=GRN),
                         T("rescaled per tile", 22, GRN)).arrange(DOWN, buff=0.15)\
                .move_to([3.8, -0.8, 0])
            self.play(FadeIn(tile), FadeIn(note, shift=0.2 * LEFT), run_time=0.6)
            for c in range(1, 4):
                self.play(tile.animate.shift(RIGHT * 0.42 * 3), run_time=b.frac(0.07))
                if c == 1:
                    self.play(FadeIn(hud, shift=0.2 * UP), run_time=0.5)
            self.play(grid.animate.set_stroke(opacity=0.15), run_time=b.frac(0.1))
        self.clear_stage()


# ---------------------------------------------------------------------------------------------
class S07_Close(ExplainerScene):
    HEADER = "The one move"

    def construct(self):
        self.show_header()
        alg = VGroup(
            M("m'", "=", r"\max(", "m", ",", "x", ")", size=54),
            M("d'", "=", "d", r"\cdot", r"e^{", "m", "-", "m'", "}", "+", r"e^{", "x", "-", "m'",
              "}", size=54),
        ).arrange(DOWN, buff=0.55, aligned_edge=LEFT).move_to(LEFT * 2.0 + UP * 0.2)
        for part in [*alg[0], *alg[1]]:
            part.set_color({"m": YEL, "m'": YEL, "d": GRN, "d'": GRN}.get(part.get_tex_string(), INK))
        alg[1][3:9].set_color(RED), alg[1][5].set_color(YEL), alg[1][7].set_color(YEL)

        # the running total: old pieces shrink by the factor, then the new leader lands on top
        U, base, x = 2.4, -2.6, 4.3
        old = [(1.0, BLUE), (0.35, BLUE), (0.12, BLUE)]
        sh, new = ValueTracker(1.0), ValueTracker(0.0)

        def draw():
            g, y = VGroup(), base
            pieces = [(h * sh.get_value(), c) for h, c in old] + [(new.get_value(), YEL)]
            for h, c in pieces:
                hh = h * U
                if hh < 1e-3:
                    continue
                g.add(Rectangle(width=0.9, height=hh, stroke_color=BG, stroke_width=2,
                                fill_color=c, fill_opacity=0.9).move_to([x, y + hh / 2, 0]))
                y += hh
            return g

        stack = always_redraw(draw)
        floor = Line([x - 0.8, base, 0], [x + 0.8, base, 0], color=GREY, stroke_width=2)
        d_lab = M("d", size=40, color=GRN).next_to(floor, DOWN, buff=0.15)

        with self.beat("g1") as b:
            self.play(Write(alg[0]), Create(floor), FadeIn(d_lab), run_time=b.frac(0.15))
            self.add(stack)
            self.play(Write(alg[1]), run_time=b.frac(0.2))
            factor = alg[1][3:9]
            self.play(flash_around(factor, RED), run_time=b.frac(0.12))
            k = factor.copy()
            self.play(k.animate.next_to([x - 0.5, base + 1.6, 0], LEFT, buff=0.1),
                      run_time=b.frac(0.1))
            self.play(sh.animate.set_value(0.135), run_time=b.frac(0.2))
            self.play(FadeOut(k), new.animate.set_value(1.0), run_time=b.frac(0.15))

        with self.beat("g2") as b:
            self.play(*dim(stack, floor, d_lab, to=0.35), run_time=b.frac(0.1))
            self.play(self.focus(alg, pad=1.5), run_time=b.frac(0.3))
            self.play(Circumscribe(alg, color=GRN, buff=0.3), run_time=b.frac(0.25))


SCENE_ORDER = ["S01_Softmax", "S02_Overflow", "S03_Passes", "S04_Online", "S05_Why",
               "S06_Merge", "S07_Close"]
