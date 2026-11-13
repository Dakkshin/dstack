"""RSA explainer scenes. Engine (palette, beat sync, icons) lives in the manim-explainer skill.

Every number on screen comes from numbers.json (written by compute.py).
"""

import os
import sys

sys.path.insert(0, os.environ.get("EXPLAINER_LIB") or
                os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "scripts"))
from explainer_lib import *  # noqa: E402,F401,F403

RSAScene = ExplainerScene


# ---------- scenes ----------

class S01_Hook(RSAScene):
    def construct(self):
        with self.beat("h1") as b:
            q = T("How can anyone lock a box\nthat only one person can open?", 48,
                  line_spacing=1.2)
            self.play(Write(q), run_time=b.frac(0.8))
        with self.beat("h2") as b:
            self.play(q.animate.scale(0.55).to_edge(UP, buff=0.5), run_time=0.8)
            box = box_icon().move_to(LEFT * 3 + DOWN * 0.3)
            you = person("you", YEL).move_to(RIGHT * 4 + DOWN * 0.1)
            k = key_icon(YEL, 0.8).next_to(you, UP, buff=0.25)
            locks = VGroup(*[padlock(BLUE, False, 0.45) for _ in range(7)])
            locks.arrange(RIGHT, buff=0.45).move_to(DOWN * 2.7)
            self.play(FadeIn(box), FadeIn(you), run_time=0.8)
            self.play(LaggedStart(*[FadeIn(l, shift=0.3 * UP) for l in locks], lag_ratio=0.15),
                      run_time=b.frac(0.22))
            lock = locks[3]
            self.play(lock.animate.scale(1.6).move_to(box.get_center() + 0.05 * DOWN),
                      run_time=b.frac(0.15))
            self.play(lock[1].animate.shift(0.28 * 1.6 * 0.45 * DOWN), run_time=0.35,
                      rate_func=rush_into)
            self.play(Flash(lock, color=BLUE, flash_radius=0.7), run_time=0.6)
            self.play(FadeIn(k, shift=0.2 * DOWN), run_time=0.6)
            self.play(Indicate(k, color=YEL, scale_factor=1.25), run_time=b.frac(0.12))
        self.clear_stage()
        with self.beat("h3") as b:
            rsa = T("RSA", 140, BLUE, weight=BOLD)
            who = T("Rivest  ·  Shamir  ·  Adleman  ·  1977", 34, INK).next_to(rsa, DOWN, buff=0.4)
            toy = T("built with numbers you can check by hand", 26, GREY).next_to(who, DOWN, buff=0.5)
            self.play(FadeIn(rsa, scale=0.8), run_time=1.0)
            self.play(Write(who), run_time=b.frac(0.3))
            self.play(FadeIn(toy), run_time=0.8)
        self.clear_stage()


class S02_Problem(RSAScene):
    HEADER = "1 · The problem"

    def construct(self):
        self.show_header()
        with self.beat("p1") as b:
            alice = person("Alice", BLUE).move_to(LEFT * 4.5 + DOWN * 0.6)
            bob = person("Bob", GRN).move_to(RIGHT * 4.5 + DOWN * 0.6)
            ka = key_icon(YEL, 0.7).next_to(alice, UP, buff=0.3)
            kb = key_icon(YEL, 0.7).next_to(bob, UP, buff=0.3)
            title = T("symmetric encryption (AES): one shared key", 32).to_edge(UP, buff=1.2)
            box = box_icon(1.4, 0.95).move_to(DOWN * 0.4)
            lk = padlock(YEL, True, 0.45).move_to(box.get_center())
            self.play(FadeIn(title), FadeIn(alice), FadeIn(bob), run_time=1.0)
            self.play(FadeIn(ka), FadeIn(kb), FadeIn(box), FadeIn(lk), run_time=1.0)
            self.play(Indicate(ka, color=YEL), Indicate(kb, color=YEL), run_time=b.frac(0.2))
        with self.beat("p2") as b:
            self.play(FadeOut(kb), FadeOut(box), FadeOut(lk), run_time=0.6)
            eve = person("Eve", RED).move_to(DOWN * 2.2)
            self.play(FadeIn(eve, shift=0.3 * UP), run_time=0.8)
            moving = ka.copy()
            path = ArcBetweenPoints(ka.get_center(), bob.get_top() + 0.6 * UP, angle=-PI / 4)
            self.play(MoveAlongPath(moving, path), run_time=b.frac(0.25))
            spy = moving.copy()
            self.play(spy.animate.next_to(eve, UP, buff=0.2).set_color(RED), run_time=b.frac(0.12))
            note = T("Eve copies the key", 28, RED).next_to(eve, RIGHT, buff=0.5)
            self.play(FadeIn(note), run_time=0.6)
        self.clear_stage()
        with self.beat("p3") as b:
            pts = [2.0 * np.array([np.cos(a), np.sin(a), 0]) + 0.6 * UP
                   for a in np.linspace(0, TAU, 12, endpoint=False)]
            dots = VGroup(*[Dot(p, color=BLUE, radius=0.07) for p in pts])
            lines = VGroup(*[Line(pts[i], pts[j], stroke_width=1.2, color=GREY)
                             for i in range(12) for j in range(i + 1, 12)])
            eq = M(r"\binom{%s}{2}" % fmt(N["people"]), "=",
                   r"\frac{%s \cdot %s}{2}" % (fmt(N["people"]), fmt(N["people"] - 1)), "=",
                   fmt(N["pair_keys"]), r"\text{ keys}", size=46).move_to(DOWN * 2.6)
            eq[4].set_color(RED)
            self.play(FadeIn(dots), run_time=0.6)
            self.play(Create(lines, lag_ratio=0.02), run_time=b.frac(0.35))
            self.play(Write(eq), run_time=b.frac(0.3))
        self.clear_stage()
        with self.beat("p4") as b:
            pub = VGroup(key_icon(BLUE, 1.3), T("public key", 34, BLUE), T("only locks", 26, GREY))
            prv = VGroup(key_icon(YEL, 1.3), T("private key", 34, YEL), T("only unlocks", 26, GREY))
            for g in (pub, prv):
                g.arrange(DOWN, buff=0.35)
            VGroup(pub, prv).arrange(RIGHT, buff=3.0).move_to(DOWN * 0.2)
            self.play(FadeIn(pub, shift=0.3 * RIGHT), run_time=b.frac(0.2))
            self.play(FadeIn(prv, shift=0.3 * LEFT), run_time=b.frac(0.2))
        self.clear_stage(keep=())


class S03_Trapdoor(RSAScene):
    HEADER = "2 · The idea"

    def construct(self):
        self.show_header()
        with self.beat("i1") as b:
            title = T("trapdoor one-way function", 40, INK).to_edge(UP, buff=1.1)
            x = Circle(0.6, color=INK).move_to(LEFT * 3.5 + DOWN * 0.2)
            fx = Circle(0.6, color=INK).move_to(RIGHT * 3.5 + DOWN * 0.2)
            lx, lfx = M("x").move_to(x), M("f(x)").move_to(fx)
            fwd = CurvedArrow(x.get_top() + 0.1 * UP, fx.get_top() + 0.1 * UP, angle=-PI / 4,
                              color=GRN)
            bwd = DashedVMobject(CurvedArrow(fx.get_bottom() + 0.1 * DOWN,
                                             x.get_bottom() + 0.1 * DOWN, angle=-PI / 4, color=RED))
            easy = T("easy", 30, GRN).next_to(fwd, UP, buff=0.15)
            hard = T("hard", 30, RED).next_to(bwd, DOWN, buff=0.15)
            trap = T("…unless you know the secret", 26, YEL).next_to(hard, DOWN, buff=0.25)
            self.play(FadeIn(title), run_time=0.6)
            self.play(Create(x), Create(fx), Write(lx), Write(lfx), run_time=1.0)
            self.play(Create(fwd), FadeIn(easy), run_time=b.frac(0.15))
            self.play(Create(bwd), FadeIn(hard), run_time=b.frac(0.15))
            self.play(FadeIn(trap), run_time=0.6)
        self.clear_stage()
        with self.beat("i2") as b:
            mul = M(str(N["p"]), r"\times", str(N["q"]), "=", fmt(N["n"]), size=80)
            mul[0].set_color(YEL)
            mul[2].set_color(YEL)
            mul[4].set_color(BLUE)
            tick = T("instant", 30, GRN).next_to(mul, DOWN, buff=0.6)
            self.play(Write(mul[:4]), run_time=b.frac(0.25))
            self.play(FadeIn(mul[4], shift=0.2 * LEFT), run_time=0.4)
            self.play(FadeIn(tick), run_time=0.5)
        with self.beat("i3") as b:
            back = M(fmt(N["n"]), "=", "?", r"\times", "?", size=80)
            back[0].set_color(BLUE)
            back[2].set_color(RED)
            back[4].set_color(RED)
            self.play(FadeOut(tick), TransformMatchingTex(mul, back), run_time=1.0)
            digits = N["N"][:180]
            lines = VGroup(*[Mono(digits[i:i + 60], 22, GREY) for i in range(0, 180, 60)])
            lines.arrange(DOWN, buff=0.12, aligned_edge=LEFT).next_to(back, DOWN, buff=0.8)
            more = T("… hundreds of digits", 26, GREY).next_to(lines, DOWN, buff=0.25)
            self.play(FadeIn(lines, lag_ratio=0.3), run_time=b.frac(0.3))
            self.play(FadeIn(more), run_time=0.5)
        self.clear_stage()
        with self.beat("i4") as b:
            fin = M(fmt(N["n"]), "=", "p", r"\times", "q", size=80)
            fin[0].set_color(BLUE)
            fin[2].set_color(YEL)
            fin[4].set_color(YEL)
            lab = T("the primes are the trapdoor", 34, YEL).next_to(fin, DOWN, buff=0.7)
            self.play(Write(fin), run_time=b.frac(0.25))
            self.play(FadeIn(lab), Circumscribe(VGroup(fin[2], fin[4]), color=YEL),
                      run_time=b.frac(0.3))
        self.clear_stage()


class S04_KeyGen(RSAScene):
    HEADER = "3 · Key generation"

    def side(self, mob, slot):
        target = mob.copy().scale(0.62)
        target.move_to(np.array([-5.3, 2.4 - 0.85 * slot, 0]))
        return target

    def construct(self):
        self.show_header()
        rail = Line(np.array([-4.2, 2.9, 0]), np.array([-4.2, -3.3, 0]), color=GREY,
                    stroke_width=1.5)
        p, q, n, phi, e, d = (N[k] for k in ("p", "q", "n", "phi", "e", "d"))
        C = RIGHT * 1.2  # centre of the work area

        with self.beat("k1") as b:
            pq = VGroup(M("p", "=", str(p)), M("q", "=", str(q))).arrange(DOWN, buff=0.4).move_to(C)
            for x in pq:
                x[2].set_color(YEL)
            self.play(Create(rail), Write(pq), run_time=b.frac(0.4))
            self.play(Transform(pq[0], self.side(pq[0], 0)), Transform(pq[1], self.side(pq[1], 1)),
                      run_time=0.8)
        with self.beat("k2") as b:
            e1 = M("n", "=", "p", r"\cdot", "q").move_to(C)
            e2 = M("n", "=", str(p), r"\cdot", str(q)).move_to(C)
            e3 = M("n", "=", fmt(n)).move_to(C)
            e3[2].set_color(BLUE)
            tag = T("public", 28, BLUE).next_to(e3, DOWN, buff=0.4)
            self.play(Write(e1), run_time=0.8)
            self.play(TransformMatchingTex(e1, e2), run_time=0.8)
            self.play(TransformMatchingTex(e2, e3), FadeIn(tag), run_time=0.8)
            self.wait(b.frac(0.2))
            self.play(Transform(e3, self.side(e3, 2)), FadeOut(tag), run_time=0.7)
        with self.beat("k3") as b:
            f1 = M(r"\varphi(n)", "=", "(p-1)(q-1)").move_to(C)
            f2 = M(r"\varphi(n)", "=", rf"{p - 1} \cdot {q - 1}").move_to(C)
            f3 = M(r"\varphi(n)", "=", fmt(phi)).move_to(C)
            f3[2].set_color(RED)
            what = T("how many numbers below n share no factor with n", 26, GREY)
            what.next_to(f3, DOWN, buff=0.5)
            tag = T("secret", 28, RED).next_to(what, DOWN, buff=0.3)
            self.play(Write(f1), run_time=1.0)
            self.play(TransformMatchingTex(f1, f2), run_time=0.8)
            self.play(TransformMatchingTex(f2, f3), run_time=0.8)
            self.play(FadeIn(what), run_time=0.6)
            self.play(FadeIn(tag), run_time=0.5)
            self.wait(b.frac(0.25))
            self.play(Transform(f3, self.side(f3, 3)), FadeOut(what), FadeOut(tag), run_time=0.7)
        with self.beat("k4") as b:
            g1 = M("e", "=", str(e)).move_to(C + 0.5 * UP)
            g1[2].set_color(BLUE)
            g2 = M(rf"\gcd({e},\ {fmt(phi)}) = 1", r"\ \checkmark").next_to(g1, DOWN, buff=0.5)
            g2[1].set_color(GRN)
            self.play(Write(g1), run_time=0.8)
            self.play(Write(g2), run_time=b.frac(0.35))
            self.play(Transform(g1, self.side(g1, 4)), FadeOut(g2), run_time=0.7)
        with self.beat("k5") as b:
            h1 = M("d", r"\equiv", "e^{-1}", r"\pmod{\varphi(n)}").move_to(C + 2.3 * UP)
            h2 = M(f"{e}", r"\cdot", "d", r"\equiv", "1", rf"\pmod{{{fmt(phi)}}}").move_to(C + 2.3 * UP)
            h2[2].set_color(YEL)
            sub = T("extended Euclidean algorithm", 30, GREY).next_to(h2, DOWN, buff=0.5)
            self.play(Write(h1), run_time=b.frac(0.25))
            self.play(TransformMatchingTex(h1, h2), run_time=1.0)
            self.play(FadeIn(sub), run_time=0.6)
        with self.beat("k6") as b:
            self.play(FadeOut(sub), h2.animate.scale(0.8).move_to(C + 2.75 * UP), run_time=0.6)
            divs = [dv for dv in N["egcd_divisions"] if dv["r"] != 0]
            rows = VGroup()
            for dv in divs:
                r = M(fmt(dv["a"]), "=", str(dv["q"]), r"\cdot", fmt(dv["b"]), "+", str(dv["r"]),
                      size=46)
                r[6].set_color(YEL)
                rows.add(r)
            rows.arrange(DOWN, buff=0.35, aligned_edge=LEFT).move_to(C + 1.0 * UP)
            for r in rows:
                self.play(Write(r), run_time=b.frac(0.7 / len(rows)))
            last = rows[-1][6]
            last.set_color(GRN)
            self.play(Circumscribe(last, color=GRN, shape=Circle), run_time=0.8)
        with self.beat("k7") as b:
            def bs_tex(row):
                x, A, y, B = row
                sign = "-" if y < 0 else "+"
                return M("1", "=", str(x), r"\cdot", fmt(A), sign, str(abs(y)), r"\cdot", fmt(B),
                         size=50)
            chain = [bs_tex(r) for r in N["backsub"]]
            for c in chain:
                c.move_to(C + 1.6 * DOWN)
            self.play(Write(chain[0]), Indicate(rows[-1], color=YEL), run_time=b.frac(0.2))
            for i in range(1, len(chain)):
                self.play(Indicate(rows[len(rows) - 1 - i], color=YEL), run_time=0.7)
                self.play(TransformMatchingTex(chain[i - 1], chain[i]), run_time=b.frac(0.18))
            fin = chain[-1]
            fin[5:7].set_color(YEL)
            self.play(Circumscribe(fin[5:7], color=YEL), run_time=0.9)
        with self.beat("k8") as b:
            t_raw = N["egcd_t_raw"]
            dd = M("d", "=", str(t_raw), "+", fmt(phi), "=", fmt(d), size=54).move_to(C + 1.0 * UP)
            dd[6].set_color(YEL)
            chk = M(rf"{e} \cdot {fmt(d)} = {fmt(N['ed'])} = {N['k']} \cdot {fmt(phi)} + 1",
                    size=40, color=GREY).next_to(dd, DOWN, buff=0.5)
            self.play(FadeOut(rows), FadeOut(h2), FadeOut(fin), run_time=0.6)
            self.play(Write(dd), run_time=b.frac(0.2))
            self.play(FadeIn(chk), run_time=0.8)
            self.wait(b.frac(0.12))
            pub = card(VGroup(T("public key", 28, BLUE),
                              M(r"(n, e) = (" + fmt(n) + ",\\ " + str(e) + ")", size=46))
                       .arrange(DOWN, buff=0.25), BLUE)
            prv = card(VGroup(T("private key", 28, YEL), M("d = " + fmt(d), size=46))
                       .arrange(DOWN, buff=0.25), YEL)
            cards = VGroup(pub, prv).arrange(RIGHT, buff=0.8).move_to(C + 1.4 * DOWN)
            self.play(FadeIn(cards, shift=0.3 * UP), run_time=b.frac(0.2))
        self.clear_stage()


class S05_EncryptDecrypt(RSAScene):
    HEADER = "4 · Encrypt and decrypt"

    def construct(self):
        self.show_header()
        n, m, e, d, c = (N[k] for k in ("n", "m", "e", "d", "c"))
        O = np.array([3.4, -0.6, 0])
        R = 2.45

        def ang(v):
            return PI / 2 - TAU * (v % n) / n

        with self.beat("c1") as b:
            f1 = M("c", "=", "m^{e}", r"\bmod", "n").to_edge(UP, buff=1.0)
            f2 = M("c", "=", f"{m}^{{{e}}}", r"\bmod", fmt(n)).to_edge(UP, buff=1.0)
            self.play(Write(f1), run_time=b.frac(0.35))
            self.play(TransformMatchingTex(f1, f2), run_time=1.0)
        with self.beat("c2") as b:
            dial = Circle(R, color=GREY, stroke_width=3).move_to(O)
            ticks = VGroup(*[
                Line(O + (R - (0.22 if i % 4 == 0 else 0.12)) * np.array([np.cos(a), np.sin(a), 0]),
                     O + R * np.array([np.cos(a), np.sin(a), 0]), color=GREY, stroke_width=2)
                for i, a in enumerate(PI / 2 - TAU * np.arange(16) / 16)])
            zero = M("0", size=34, color=GREY).next_to(dial, UP, buff=0.12)
            cap = T(f"{n:,} positions", 24, GREY).next_to(dial, DOWN, buff=0.25)
            tracker = ValueTracker(0)
            hand = always_redraw(lambda: Line(
                O, O + (R - 0.3) * np.array([np.cos(tracker.get_value()),
                                              np.sin(tracker.get_value()), 0]),
                color=YEL, stroke_width=5))
            tip = always_redraw(lambda: Dot(
                O + (R - 0.3) * np.array([np.cos(tracker.get_value()),
                                           np.sin(tracker.get_value()), 0]), color=YEL,
                radius=0.08))
            tracker.set_value(PI / 2)
            self.play(Create(dial), Create(ticks), FadeIn(zero), FadeIn(cap), run_time=1.0)
            self.add(hand, tip)
            self.play(tracker.animate.set_value(PI / 2 - TAU), run_time=b.frac(0.35),
                      rate_func=smooth)
            self.play(tracker.animate.set_value(ang(m)), run_time=0.6)

        def spin_to(value, wraps, rt):
            cur = tracker.get_value()
            target = ang(value)
            delta = (cur - target) % TAU + TAU * min(wraps, 2)
            self.play(tracker.animate.set_value(cur - delta), run_time=rt, rate_func=smooth)

        with self.beat("c3") as b:
            tr = N["enc_trace"]
            rows = VGroup()
            power = 1
            exprs = [M(f"{m}^{{1}}", "=", str(m), size=40)]
            exprs.append(M(f"{m}^{{2}}", "=", fmt(N["m_sq"]), r"\equiv", fmt(N["m_sq_r"]), size=40))
            power = 2
            for st in tr[2:]:
                if st["op"] == "S":
                    power *= 2
                    exprs.append(M(f"{m}^{{{power}}}", r"\equiv", fmt(st["value"]), size=40))
                else:
                    prev = tr[tr.index(st) - 1]["value"]
                    exprs.append(M(f"{m}^{{{power + 1}}}", r"\equiv",
                                   rf"{fmt(prev)} \cdot {m}", r"\equiv", fmt(st["value"]), size=40))
            rows = VGroup(*exprs).arrange(DOWN, buff=0.3, aligned_edge=LEFT)
            rows.move_to(np.array([-3.2, -0.7, 0]))
            step_rt = (b.dur - 0.5) / len(exprs)
            self.play(FadeIn(rows[0]), run_time=0.5)
            prev_val = m
            for row, st in zip(rows[1:], tr[1:]):
                v = st["value"]
                raw = prev_val * prev_val if st["op"] == "S" else prev_val * m
                self.play(FadeIn(row, shift=0.15 * DOWN), run_time=0.4)
                spin_to(v, raw // n, max(0.6, step_rt - 0.5))
                prev_val = v
        with self.beat("c4") as b:
            last = rows[-1]
            last[-1].set_color(YEL)
            big = M("c", "=", fmt(c), size=64, color=YEL)
            big.move_to(np.array([-3.2, 2.0, 0]))
            self.play(Circumscribe(last[-1], color=YEL), run_time=0.8)
            self.play(FadeOut(f2), TransformFromCopy(last[-1], big[2]), FadeIn(big[:2]),
                      rows.animate.set_opacity(0.35), run_time=b.frac(0.4))
        with self.beat("c5") as b:
            g = M("m", "=", f"{fmt(c)}^{{{fmt(d)}}}", r"\bmod", fmt(n), size=52).to_edge(UP, buff=1.0)
            self.play(FadeOut(rows), FadeOut(big), Write(g), run_time=b.frac(0.3))
            spin_to(N["m_back"], 2, b.frac(0.4))
            res = M("m", "=", str(N["m_back"]), size=72, color=GRN).move_to(np.array([-3.2, -0.6, 0]))
            self.play(Write(res), Flash(tip.get_center(), color=GRN), run_time=0.8)
        self.clear_stage()


class S06_WhyItWorks(RSAScene):
    HEADER = "5 · Why it works"

    def construct(self):
        self.show_header()
        e, d, phi, k = N["e"], N["d"], N["phi"], N["k"]
        with self.beat("w1") as b:
            a1 = M("e", r"\,", "d", "=", rf"{e} \cdot {fmt(d)}", "=", fmt(N["ed"]), size=56)
            a2 = M("e", r"\,", "d", "=", "1", "+", rf"{k} \cdot {fmt(phi)}", size=56)
            a3 = M("e", r"\,", "d", "=", "1", "+", r"k\,\varphi(n)", size=56)
            for a in (a1, a2, a3):
                a.move_to(UP * 0.6)
            a3[4].set_color(YEL)
            self.play(Write(a1), run_time=b.frac(0.3))
            self.play(TransformMatchingTex(a1, a2), run_time=1.0)
            self.wait(b.frac(0.15))
            self.play(TransformMatchingTex(a2, a3), run_time=1.0)
        with self.beat("w2") as b:
            self.play(a3.animate.scale(0.6).to_edge(UP, buff=1.0), run_time=0.7)
            q1 = M("c^{d}", "=", "(m^{e})^{d}", "=", "m^{ed}", size=60)
            q2 = M("c^{d}", "=", r"m^{1 + k\varphi(n)}", size=60)
            q3 = M("c^{d}", "=", "m", r"\cdot", r"\left(m^{\varphi(n)}\right)^{k}", size=60)
            for q in (q1, q2, q3):
                q.move_to(DOWN * 0.4)
            self.play(Write(q1), run_time=b.frac(0.25))
            self.play(TransformMatchingTex(q1, q2), run_time=1.0)
            self.play(TransformMatchingTex(q2, q3), run_time=1.0)
        with self.beat("w3") as b:
            th = M(r"\gcd(m, n) = 1", r"\;\Longrightarrow\;", r"m^{\varphi(n)} \equiv 1 \pmod{n}",
                   size=46)
            lab = T("Euler's theorem", 26, BLUE)
            box = card(VGroup(lab, th).arrange(DOWN, buff=0.25), BLUE).move_to(DOWN * 2.5)
            self.play(FadeIn(box, shift=0.2 * UP), run_time=b.frac(0.3))
            self.play(Indicate(q3[4], color=BLUE), Indicate(th[2], color=BLUE), run_time=1.2)
        with self.beat("w4") as b:
            q4 = M("c^{d}", r"\equiv", "m", r"\cdot", "1^{k}", size=60).move_to(q3)
            q5 = M("c^{d}", r"\equiv", "m", r"\pmod{n}", size=60).move_to(q3)
            q5[2].set_color(GRN)
            self.play(TransformMatchingTex(q3, q4), run_time=1.0)
            self.play(TransformMatchingTex(q4, q5), run_time=1.0)
            self.play(Create(SurroundingRectangle(q5, color=GRN, buff=0.2)), run_time=b.frac(0.2))
        self.clear_stage()
        with self.beat("w5") as b:
            top = T("what if m shares a factor with n?", 32, YEL).to_edge(UP, buff=1.1)
            lp = M(r"m^{ed} \equiv m \pmod{p}", size=48)
            lq = M(r"m^{ed} \equiv m \pmod{q}", size=48)
            pair = VGroup(lp, lq).arrange(DOWN, buff=0.5).move_to(LEFT * 4.0 + DOWN * 0.3)
            fer = T("Fermat, each prime alone", 24, GREY).next_to(pair, DOWN, buff=0.35)
            arrow = Arrow(pair.get_right(), pair.get_right() + 1.8 * RIGHT, color=BLUE, buff=0.25)
            crt = T("CRT", 26, BLUE).next_to(arrow, UP, buff=0.1)
            res = M(r"m^{ed} \equiv m \pmod{pq}", size=48, color=GRN).next_to(arrow, RIGHT, buff=0.25)
            self.play(FadeIn(top), run_time=0.7)
            self.play(Write(pair), FadeIn(fer), run_time=b.frac(0.35))
            self.play(GrowArrow(arrow), FadeIn(crt), run_time=0.7)
            self.play(Write(res), run_time=b.frac(0.2))
        self.clear_stage()


class S07_Security(RSAScene):
    HEADER = "6 · Why it is secure"

    def construct(self):
        self.show_header()
        n = N["n"]
        with self.beat("s1") as b:
            chain = M("d", r"\;\Longleftarrow\;", r"\varphi(n)", r"\;\Longleftarrow\;", "p,\\ q",
                      r"\;\Longleftarrow\;", r"\text{factor } n", size=58)
            chain[0].set_color(YEL)
            chain[4].set_color(YEL)
            chain[6].set_color(RED)
            sees = T("attacker sees only  n  and  e", 30, BLUE).next_to(chain, UP, buff=0.9)
            self.play(FadeIn(sees), run_time=0.7)
            self.play(LaggedStart(*[Write(x) for x in chain], lag_ratio=0.3), run_time=b.frac(0.6))
        self.clear_stage()
        with self.beat("s2") as b:
            kt = ValueTracker(2)
            label = always_redraw(lambda: M(
                fmt(n), r"\bmod", str(int(kt.get_value())), "=", str(n % int(kt.get_value())),
                size=60, color=GRN if n % int(kt.get_value()) == 0 else INK).move_to(UP * 0.5))
            count = always_redraw(lambda: T(
                f"candidates tested: {int(kt.get_value()) - 1}", 28, GREY).move_to(DOWN * 0.9))
            self.add(label, count)
            self.play(kt.animate.set_value(N["trial_found"]), run_time=b.frac(0.55),
                      rate_func=linear)
            self.remove(label, count)
            label_f = M(fmt(n), r"\bmod", str(N["trial_found"]), "=", "0", size=60,
                        color=GRN).move_to(UP * 0.5)
            count_f = T(f"candidates tested: {N['trial_count']}", 28, GREY).move_to(DOWN * 0.9)
            self.add(label_f, count_f)
            fac = M(fmt(n), "=", str(N["p"]), r"\times", str(N["q"]), size=52).move_to(DOWN * 2.2)
            self.play(Write(fac), run_time=0.8)
        self.clear_stage()
        with self.beat("s3") as b:
            s = N["N"]
            w = 62
            lines = VGroup(*[Mono(s[i:i + w], 20, BLUE) for i in range(0, len(s), w)])
            lines.arrange(DOWN, buff=0.1, aligned_edge=LEFT)
            lines.scale_to_fit_width(min(lines.width, 12.0)).move_to(DOWN * 0.3)
            cap = T(f"a real modulus:  {N['N_bits']} bits,  {N['N_digits']} digits", 30, INK)
            cap.next_to(lines, UP, buff=0.4)
            self.play(FadeIn(cap), run_time=0.6)
            self.play(LaggedStart(*[FadeIn(l) for l in lines], lag_ratio=0.15), run_time=b.frac(0.5))
        with self.beat("s4") as b:
            self.play(FadeOut(lines), FadeOut(cap), run_time=0.6)
            root = T(f"trial division: search up to √n, a {N['sqrtN_digits']}-digit number",
                     30, INK).to_edge(UP, buff=1.1)
            scale = 9.0 / N["N_bits"]
            y0 = 0.4
            bar1 = Rectangle(width=N["rsa250_bits"] * scale, height=0.55, fill_color=GRN,
                             fill_opacity=0.85, stroke_width=0)
            bar2 = Rectangle(width=N["N_bits"] * scale, height=0.55, fill_color=BLUE,
                             fill_opacity=0.85, stroke_width=0)
            for bar, y in ((bar1, y0), (bar2, y0 - 1.3)):
                bar.move_to(np.array([-4.0 + bar.width / 2, y, 0]))
            t1 = T(f"RSA-{N['rsa250_digits']}:  {N['rsa250_bits']} bits  (factored {N['rsa250_year']})",
                   24, GRN).next_to(bar1, UP, buff=0.15, aligned_edge=LEFT)
            t2 = T(f"a TLS key today:  {N['N_bits']} bits", 24, BLUE).next_to(bar2, UP, buff=0.15,
                                                                           aligned_edge=LEFT)
            cost = T(f"≈ {N['rsa250_core_years']:,} CPU core-years with the number field sieve",
                     26, GREY).move_to(DOWN * 2.4)
            self.play(FadeIn(root), run_time=b.frac(0.15))
            self.play(GrowFromEdge(bar1, LEFT), FadeIn(t1), run_time=b.frac(0.25))
            self.play(FadeIn(cost), run_time=0.7)
            self.play(GrowFromEdge(bar2, LEFT), FadeIn(t2), run_time=b.frac(0.2))
        self.clear_stage()
        with self.beat("s5") as b:
            a = T(f"{N['N_bits']}-bit RSA  ≈  112-bit security", 40, BLUE).move_to(UP * 1.2)
            src = T("NIST SP 800-57", 22, GREY).next_to(a, DOWN, buff=0.2)
            shor = T("large quantum computer + Shor's algorithm  →  factors n efficiently", 30, RED)
            shor.move_to(DOWN * 0.6)
            pq = T("response: post-quantum ML-KEM (FIPS 203)", 30, GRN).next_to(shor, DOWN, buff=0.5)
            self.play(FadeIn(a), FadeIn(src), run_time=b.frac(0.2))
            self.play(FadeIn(shor), run_time=b.frac(0.2))
            self.play(FadeIn(pq), run_time=b.frac(0.15))
        self.clear_stage()


class S08_Efficiency(RSAScene):
    HEADER = "7 · Efficiency"

    def bit_row(self, bits, size=0.6, color=INK):
        cells = VGroup()
        for ch in bits:
            sq = Square(size, color=GREY, stroke_width=2)
            t = M(ch, size=40, color=YEL if ch == "1" else color).move_to(sq)
            cells.add(VGroup(sq, t))
        cells.arrange(RIGHT, buff=0.08)
        return cells

    def construct(self):
        self.show_header()
        d = N["d"]
        with self.beat("f1") as b:
            naive = M(rf"{fmt(N['c'])}^{{{fmt(d)}}}", "=", r"\underbrace{c \cdot c \cdots c}"
                      + rf"_{{{fmt(N['naive_mults_d'])}\text{{ multiplications}}}}", size=54)
            naive.move_to(UP * 0.5)
            no = T(f"at {N['N_bits']} bits, d itself has ~{N['N_bits']} bits: hopeless", 28, RED)
            no.next_to(naive, DOWN, buff=0.7)
            self.play(Write(naive), run_time=b.frac(0.35))
            self.play(FadeIn(no), run_time=0.8)
        self.clear_stage()
        with self.beat("f2") as b:
            bits = N["d_bits"]
            title = M(fmt(d), "=", r"\texttt{" + bits + r"}_2", size=50).to_edge(UP, buff=1.1)
            row = self.bit_row(bits).move_to(UP * 0.4)
            ops = VGroup()
            for i, ch in enumerate(bits):
                lab = "" if i == 0 else ("S M" if ch == "1" else "S")
                t = T(lab or "start", 20, GRN if ch == "1" else GREY).next_to(row[i], DOWN, buff=0.2)
                ops.add(t)
            sq_ct = N["dec_squarings"]
            mu_ct = N["dec_mults"]
            tally = VGroup(T(f"{sq_ct} squarings", 32, INK), T(f"{mu_ct} multiplies", 32, GRN),
                           T(f"instead of {N['naive_mults_d']:,}", 32, RED)).arrange(RIGHT, buff=0.8)
            tally.move_to(DOWN * 2.2)
            self.play(Write(title), FadeIn(row), run_time=b.frac(0.2))
            ptr = SurroundingRectangle(row[0], color=YEL, buff=0.05)
            self.play(Create(ptr), FadeIn(ops[0]), run_time=0.5)
            step = b.frac(0.45) / (len(bits) - 1)
            for i in range(1, len(bits)):
                self.play(ptr.animate.move_to(row[i]), FadeIn(ops[i]), run_time=step)
            self.play(FadeOut(ptr), LaggedStart(*[FadeIn(t) for t in tally], lag_ratio=0.4),
                      run_time=b.frac(0.2))
        self.clear_stage()
        with self.beat("f3") as b:
            fb = N["f4_bits"]
            title = M("e", "=", fmt(N["F4"]), "=", "2^{16} + 1", size=54).to_edge(UP, buff=1.1)
            row = self.bit_row(fb, 0.55).move_to(UP * 0.2)
            cost = T(f"{N['f4_squarings']} squarings + {N['f4_mults']} multiply", 34, GRN)
            cost.next_to(row, DOWN, buff=0.8)
            why = T("fast encryption and signature checks", 26, GREY).next_to(cost, DOWN, buff=0.3)
            self.play(Write(title), run_time=b.frac(0.2))
            self.play(LaggedStart(*[FadeIn(c) for c in row], lag_ratio=0.05), run_time=b.frac(0.25))
            self.play(FadeIn(cost), FadeIn(why), run_time=b.frac(0.15))
        self.clear_stage()
        with self.beat("f4") as b:
            p, q, c = N["p"], N["q"], N["c"]
            lab = T("decryption with the Chinese remainder theorem", 30, BLUE).to_edge(UP, buff=1.1)
            r1 = M(r"m_1 = c^{d_p} \bmod p", "=", rf"{fmt(c)}^{{{N['dp']}}} \bmod {p}", "=",
                   str(N["m1"]), size=44)
            r2 = M(r"m_2 = c^{d_q} \bmod q", "=", rf"{fmt(c)}^{{{N['dq']}}} \bmod {q}", "=",
                   str(N["m2"]), size=44)
            r3 = M(r"m = m_2 + q\,h", "=", rf"{N['m2']} + {q} \cdot {N['h']}", "=",
                   str(N["m"]), size=44)
            grp = VGroup(r1, r2, r3).arrange(DOWN, buff=0.45, aligned_edge=LEFT).move_to(DOWN * 0.1)
            r3[4].set_color(GRN)
            note = T("two half-size exponents  ≈  4× faster", 28, GRN).move_to(DOWN * 2.7)
            self.play(FadeIn(lab), run_time=0.6)
            self.play(Write(r1), run_time=b.frac(0.2))
            self.play(Write(r2), run_time=b.frac(0.2))
            self.play(Write(r3), run_time=b.frac(0.15))
            self.play(FadeIn(note), run_time=0.6)
        self.clear_stage()
        with self.beat("f5") as b:
            rsa = card(T("RSA", 36, YEL), YEL, 0.3)
            key = VGroup(key_icon(YEL, 0.6), T("AES key", 24, YEL)).arrange(DOWN, buff=0.15)
            aes = card(T("AES", 36, GRN), GRN, 0.3)
            data = card(T("gigabytes of data", 26, INK), GREY, 0.25)
            flow = VGroup(rsa, key, aes, data).arrange(RIGHT, buff=0.9).move_to(UP * 0.2)
            arrows = VGroup(*[Arrow(flow[i].get_right(), flow[i + 1].get_left(), buff=0.12,
                                    color=GREY) for i in range(3)])
            s1 = T("slow, tiny payload", 22, GREY).next_to(rsa, DOWN, buff=0.4)
            s2 = T("fast, bulk", 22, GREY).next_to(aes, DOWN, buff=0.4)
            hyb = T("hybrid encryption", 32, INK).to_edge(UP, buff=1.2)
            self.play(FadeIn(hyb), run_time=0.6)
            self.play(LaggedStart(FadeIn(rsa), GrowArrow(arrows[0]), FadeIn(key), GrowArrow(arrows[1]),
                                  FadeIn(aes), GrowArrow(arrows[2]), FadeIn(data), lag_ratio=0.35),
                      run_time=b.frac(0.45))
            self.play(FadeIn(s1), FadeIn(s2), run_time=0.7)
        self.clear_stage()


class S09_Breaks(RSAScene):
    HEADER = "8 · Where it breaks"

    def construct(self):
        self.show_header()
        with self.beat("x1") as b:
            tb = VGroup(T("textbook RSA", 40, INK), M(r"c = m^{e} \bmod n", size=56)).arrange(DOWN, buff=0.4)
            tb.move_to(UP * 0.9)
            stamp = T("NOT SECURE", 54, RED, weight=BOLD).rotate(-0.08).next_to(tb, DOWN, buff=0.8)
            frame = SurroundingRectangle(stamp, color=RED, buff=0.15, stroke_width=5)
            self.play(FadeIn(tb), run_time=b.frac(0.3))
            self.play(FadeIn(VGroup(stamp, frame), scale=1.4), run_time=0.5)
        self.clear_stage()
        with self.beat("x2") as b:
            seen = VGroup(T("intercepted c:", 26, GREY), Mono(N["c_yes_head"] + "…", 26, INK)).arrange(RIGHT, buff=0.3)
            seen.to_edge(UP, buff=1.2)
            y = VGroup(T('Enc("YES") =', 26, INK), Mono(N["c_yes_head"] + "…", 26, INK)).arrange(RIGHT, buff=0.3)
            nn = VGroup(T('Enc("NO")  =', 26, INK), Mono(N["c_no_head"] + "…", 26, INK)).arrange(RIGHT, buff=0.3)
            VGroup(y, nn).arrange(DOWN, buff=0.5, aligned_edge=LEFT).move_to(DOWN * 0.4)
            eve = T("attacker re-encrypts each guess with the public key", 26, RED).to_edge(DOWN, buff=0.8)
            self.play(FadeIn(seen), run_time=0.8)
            self.play(FadeIn(eve), run_time=0.6)
            self.play(FadeIn(y), FadeIn(nn), run_time=b.frac(0.25))
            match = SurroundingRectangle(y, color=GRN, buff=0.12)
            self.play(Create(match), y[1].animate.set_color(GRN), seen[1].animate.set_color(GRN),
                      nn.animate.set_opacity(0.35), run_time=b.frac(0.15))
        self.clear_stage()
        with self.beat("x3") as b:
            scale = 10.0 / N["N_bits"]
            nb = Rectangle(width=N["N_bits"] * scale, height=0.5, fill_color=BLUE, fill_opacity=0.8, stroke_width=0)
            mb = Rectangle(width=N["e3_c_bits"] * scale, height=0.5, fill_color=YEL, fill_opacity=0.9, stroke_width=0)
            nb.move_to(np.array([-5.0 + nb.width / 2, 1.2, 0]))
            mb.move_to(np.array([-5.0 + mb.width / 2, 0.0, 0]))
            tn = T(f"n:  {N['N_bits']} bits", 24, BLUE).next_to(nb, UP, buff=0.12, aligned_edge=LEFT)
            tm = T(f"m³:  {N['e3_c_bits']} bits   (e = 3, no padding)", 24, YEL).next_to(mb, RIGHT, buff=0.3)
            nowrap = T("m³ < n, so nothing wraps: c = m³ exactly", 28, RED).move_to(DOWN * 1.3)
            root = M(r"\sqrt[3]{c}", "=", "m", size=50).move_to(DOWN * 2.5 + LEFT * 1.5)
            txt = T(f'= "{N["e3_secret_text"]}"', 32, GRN).next_to(root, RIGHT, buff=0.4)
            self.play(GrowFromEdge(nb, LEFT), FadeIn(tn), run_time=0.8)
            self.play(GrowFromEdge(mb, LEFT), FadeIn(tm), run_time=b.frac(0.15))
            self.play(FadeIn(nowrap), run_time=b.frac(0.12))
            self.play(Write(root), run_time=0.8)
            self.play(FadeIn(txt), run_time=0.6)
        self.clear_stage()
        with self.beat("x4") as b:
            bits = N["d_bits"]
            base = 0.55
            bars = VGroup()
            for i, ch in enumerate(bits[1:]):
                h = base * (2 if ch == "1" else 1)
                bars.add(Rectangle(width=0.55, height=h, fill_color=RED if ch == "1" else GREY,
                                   fill_opacity=0.9, stroke_width=0))
            bars.arrange(RIGHT, buff=0.12, aligned_edge=DOWN).move_to(UP * 0.6)
            labels = VGroup(*[M(ch, size=34, color=YEL if ch == "1" else INK).next_to(bar, DOWN, buff=0.15)
                              for ch, bar in zip(bits[1:], bars)])
            cap = T("time per bit of d  (after the first bit)", 24, GREY).next_to(bars, UP, buff=0.4)
            who = T("Kocher, 1996: timing leaks the private key", 28, RED).move_to(DOWN * 1.5)
            fix = VGroup(T("fix: constant-time code + blinding", 28, GRN),
                         M(r"c' = c \cdot r^{e} \bmod n", size=40, color=GRN)).arrange(RIGHT, buff=0.5)
            fix.move_to(DOWN * 2.5)
            self.play(FadeIn(cap), LaggedStart(*[GrowFromEdge(x, DOWN) for x in bars], lag_ratio=0.1),
                      FadeIn(labels), run_time=b.frac(0.3))
            self.play(FadeIn(who), run_time=0.8)
            self.play(FadeIn(fix), run_time=b.frac(0.15))
        self.clear_stage()
        with self.beat("x5") as b:
            title = T("OAEP padding", 34, GRN).to_edge(UP, buff=0.75)
            sd = card(T("random seed", 24, YEL), YEL, 0.2).move_to(LEFT * 3.4 + UP * 1.7)
            db = card(T("hash ‖ 00…00 ‖ 01 ‖ message", 24, INK), INK, 0.2).move_to(RIGHT * 2.9 + UP * 1.7)
            g = card(T("G", 28, BLUE), BLUE, 0.18).move_to(LEFT * 0.4 + UP * 0.65)
            xs = M(r"\oplus", size=50).move_to(LEFT * 3.4 + DOWN * 0.4)
            h = card(T("H", 28, BLUE), BLUE, 0.18).move_to(LEFT * 0.4 + DOWN * 0.4)
            xd = M(r"\oplus", size=50).move_to(RIGHT * 2.9 + DOWN * 0.4)
            out = card(T("00  ‖  masked seed  ‖  masked data   →   c = (·)ᵉ mod n", 24, GRN), GRN, 0.2)
            out.move_to(DOWN * 2.2)
            a = VGroup(
                Arrow(sd.get_bottom() + 0.6 * RIGHT, g.get_left(), buff=0.1, color=GREY),
                Arrow(g.get_right(), xd.get_corner(UL), buff=0.1, color=GREY),
                Arrow(np.array([xd.get_x(), db.get_bottom()[1], 0]), xd.get_top(), buff=0.1, color=GREY),
                Arrow(xd.get_left(), h.get_right(), buff=0.1, color=GREY),
                Arrow(h.get_left(), xs.get_right(), buff=0.1, color=GREY),
                Arrow(np.array([xs.get_x(), sd.get_bottom()[1], 0]), xs.get_top(), buff=0.1, color=GREY),
                Arrow(xs.get_bottom(), np.array([xs.get_x(), out.get_top()[1], 0]), buff=0.1, color=GREY),
                Arrow(xd.get_bottom(), np.array([xd.get_x(), out.get_top()[1], 0]), buff=0.1, color=GREY),
            )
            x1, x2 = xd, xs
            self.play(FadeIn(title), FadeIn(db), FadeIn(sd), run_time=b.frac(0.15))
            self.play(FadeIn(g), GrowArrow(a[0]), GrowArrow(a[1]), GrowArrow(a[2]), FadeIn(x1),
                      run_time=b.frac(0.2))
            self.play(FadeIn(h), GrowArrow(a[3]), GrowArrow(a[4]), GrowArrow(a[5]), FadeIn(x2),
                      run_time=b.frac(0.2))
            self.play(GrowArrow(a[6]), GrowArrow(a[7]), FadeIn(out), run_time=b.frac(0.15))
        self.clear_stage()
        with self.beat("x6") as b:
            l1 = VGroup(T("1998", 34, YEL), T("Bleichenbacher: PKCS#1 v1.5 padding oracle", 28, INK)).arrange(RIGHT, buff=0.5)
            l2 = VGroup(T("2017", 34, YEL), T("ROBOT: the same attack, still live on TLS servers", 28, INK)).arrange(RIGHT, buff=0.5)
            VGroup(l1, l2).arrange(DOWN, buff=0.6, aligned_edge=LEFT).move_to(UP * 0.4)
            rule = T("encrypt with OAEP  ·  sign with PSS", 32, GRN).move_to(DOWN * 2.0)
            self.play(FadeIn(l1, shift=0.2 * RIGHT), run_time=b.frac(0.25))
            self.play(FadeIn(l2, shift=0.2 * RIGHT), run_time=b.frac(0.25))
            self.play(FadeIn(rule), run_time=0.7)
        self.clear_stage()


class S10_RealWorld(RSAScene):
    HEADER = "9 · Real world"

    def construct(self):
        self.show_header()
        n, e = N["n"], N["e"]
        with self.beat("r1") as b:
            s1 = VGroup(T("sign (private d)", 28, YEL), M(r"s = H(m)^{d} \bmod n", size=54)).arrange(DOWN, buff=0.3)
            s2 = VGroup(T("verify (public e)", 28, BLUE), M(r"s^{e} \bmod n \stackrel{?}{=} H(m)", size=54)).arrange(DOWN, buff=0.3)
            VGroup(s1, s2).arrange(DOWN, buff=0.9).move_to(DOWN * 0.2)
            self.play(FadeIn(s1), run_time=b.frac(0.35))
            self.play(FadeIn(s2), run_time=b.frac(0.3))
        self.clear_stage()
        with self.beat("r2") as b:
            l1 = M(rf"H(\text{{{N['sig_msg']}}}) \bmod {fmt(n)}", "=", fmt(N["sig_hash_mod_n"]), size=48)
            l2 = M(rf"s = {fmt(N['sig_hash_mod_n'])}^{{{fmt(N['d'])}}} \bmod {fmt(n)}", "=", fmt(N["sig"]), size=48)
            l3 = M(rf"{fmt(N['sig'])}^{{{e}}} \bmod {fmt(n)}", "=", fmt(N["sig_check"]), r"\ \checkmark", size=48)
            g = VGroup(l1, l2, l3).arrange(DOWN, buff=0.5, aligned_edge=LEFT).move_to(UP * 0.2)
            l2[2].set_color(YEL)
            l3[2:].set_color(GRN)
            note = T("toy example: real RSA signs a padded SHA-256 hash (PSS)", 22, GREY).to_edge(DOWN, buff=0.7)
            self.play(Write(l1), run_time=b.frac(0.2))
            self.play(Write(l2), run_time=b.frac(0.2))
            self.play(Write(l3), FadeIn(note), run_time=b.frac(0.25))
        self.clear_stage()
        with self.beat("r3") as b:
            names = [("Root CA  (already in your browser)", YEL),
                     ("Intermediate CA", BLUE),
                     ("example.com  +  its public key", GRN)]
            boxes = VGroup(*[card(T(s, 26, c), c, 0.22) for s, c in names]).arrange(DOWN, buff=0.75)
            boxes.move_to(DOWN * 0.25)
            arr = VGroup(*[Arrow(boxes[i].get_bottom(), boxes[i + 1].get_top(), buff=0.08, color=GREY)
                           for i in range(2)])
            signs = VGroup(*[T("signs", 22, GREY).next_to(a, RIGHT, buff=0.2) for a in arr])
            self.play(FadeIn(boxes[2]), run_time=0.7)
            self.play(FadeIn(boxes[1]), GrowArrow(arr[1]), FadeIn(signs[1]), run_time=b.frac(0.2))
            self.play(FadeIn(boxes[0]), GrowArrow(arr[0]), FadeIn(signs[0]), run_time=b.frac(0.2))
        self.clear_stage()
        with self.beat("r4") as b:
            head = T("TLS 1.3", 40, INK).to_edge(UP, buff=1.1)
            gone = T("RSA key transport", 30, RED)
            strike = Line(gone.get_left(), gone.get_right(), color=RED, stroke_width=4)
            gone_g = VGroup(VGroup(gone, strike), T("removed in TLS 1.3", 24, RED)).arrange(RIGHT, buff=0.5)
            ke = T("session key:  ephemeral (EC)DHE  →  forward secrecy", 30, GRN)
            sg = T("RSA's job:  sign the handshake  (RSA-PSS, CertificateVerify)", 30, BLUE)
            col = VGroup(gone_g, ke, sg).arrange(DOWN, buff=0.7, aligned_edge=LEFT).move_to(DOWN * 0.3)
            self.play(FadeIn(head), run_time=0.6)
            self.play(FadeIn(gone), run_time=0.6)
            self.play(Create(strike), FadeIn(gone_g[1]), run_time=b.frac(0.12))
            self.play(FadeIn(ke), run_time=b.frac(0.2))
            self.play(FadeIn(sg), run_time=b.frac(0.2))
        self.clear_stage()
        with self.beat("r5") as b:
            items = [("Windows", "Authenticode"), ("Linux", "apt / rpm package signatures"),
                     ("Firmware", "Secure Boot")]
            cards = VGroup(*[card(VGroup(T(a, 30, BLUE), T(s, 22, INK)).arrange(DOWN, buff=0.2), BLUE, 0.3)
                             for a, s in items]).arrange(RIGHT, buff=0.6).move_to(UP * 0.3)
            under = T("verify the signature before running the code", 28, GRN).next_to(cards, DOWN, buff=0.8)
            self.play(LaggedStart(*[FadeIn(c, shift=0.2 * UP) for c in cards], lag_ratio=0.3),
                      run_time=b.frac(0.4))
            self.play(FadeIn(under), run_time=0.7)
        self.clear_stage()


class S11_Recap(RSAScene):
    HEADER = "10 · The viva answer"

    def construct(self):
        self.show_header()
        with self.beat("z1") as b:
            title = T("RSA in five lines", 40, YEL).to_edge(UP, buff=0.95)
            self.play(Write(title), run_time=b.frac(0.4))
        bullets = [
            ("z2", r"\textbf{Keys: } $n = pq$, \ $e$ public, \ $d \equiv e^{-1} \pmod{\varphi(n)}$"),
            ("z3", r"\textbf{Use: } $c = m^{e} \bmod n$, \quad $m = c^{d} \bmod n$"),
            ("z4", r"\textbf{Works: } $ed = 1 + k\varphi(n)$, so Euler gives $m^{ed} \equiv m$"),
            ("z5", r"\textbf{Secure: } $d$ needs $\varphi(n)$ needs $p, q$: factoring "
                   + str(N["N_bits"]) + r"-bit $n$ is infeasible"),
            ("z6", r"\textbf{Practice: } OAEP / PSS, constant time, keys and signatures only"),
        ]
        rows = VGroup()
        for i, (_, tex) in enumerate(bullets):
            num = T(f"{i + 1}", 30, BLUE)
            body = Tex(tex, font_size=42, color=INK)
            rows.add(VGroup(num, body).arrange(RIGHT, buff=0.35))
        rows.arrange(DOWN, buff=0.42, aligned_edge=LEFT)
        if rows.width > 12.2:
            rows.scale_to_fit_width(12.2)
        rows.move_to(DOWN * 0.35)
        frame = SurroundingRectangle(rows, color=GREY, buff=0.4, corner_radius=0.2, stroke_width=2)
        self.play(Create(frame), run_time=0.6)
        for (bid, _), row in zip(bullets, rows):
            with self.beat(bid) as b:
                self.play(FadeIn(row, shift=0.2 * RIGHT), run_time=min(1.0, b.frac(0.3)))
        self.wait(1.0)
        self.clear_stage()
        with self.beat("z7") as b:
            lock = padlock(BLUE, True, 1.4).move_to(LEFT * 1.6 + UP * 0.4)
            key = key_icon(YEL, 1.4).move_to(RIGHT * 1.6 + UP * 0.4)
            line = T("a lock anyone can close, a key only one person holds", 30, INK).move_to(DOWN * 1.6)
            self.play(FadeIn(lock), FadeIn(key), run_time=b.frac(0.25))
            self.play(Write(line), run_time=b.frac(0.35))
        self.play(*[FadeOut(m) for m in self.mobjects], run_time=1.2)


SCENE_ORDER = [
    "S01_Hook", "S02_Problem", "S03_Trapdoor", "S04_KeyGen", "S05_EncryptDecrypt",
    "S06_WhyItWorks", "S07_Security", "S08_Efficiency", "S09_Breaks", "S10_RealWorld", "S11_Recap",
]
