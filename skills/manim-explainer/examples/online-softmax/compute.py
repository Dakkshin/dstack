"""Every number shown or spoken in the online softmax video, with asserts."""

import json
import math
from pathlib import Path

import numpy as np

OUT = Path(__file__).with_name("numbers.json")


def r(x, k=3):
    return round(float(x), k)


def main():
    x = [3, 1, 5, 2, 7, 4]
    n = len(x)

    # plain softmax
    ex = [math.exp(v) for v in x]
    p = [e / sum(ex) for e in ex]
    assert abs(sum(p) - 1) < 1e-12

    # overflow limits: largest score whose exponential is still finite
    fp16_max = float(np.finfo(np.float16).max)
    fp32_max = float(np.finfo(np.float32).max)
    ln16, ln32 = math.log(fp16_max), math.log(fp32_max)
    with np.errstate(over="ignore"):
        assert np.isinf(np.exp(np.float16(12))) and np.isfinite(np.exp(np.float16(11)))
        assert np.isinf(np.exp(np.float32(89))) and np.isfinite(np.exp(np.float32(88)))

    # safe softmax: subtract the max, same answer
    m = max(x)
    safe = [math.exp(v - m) for v in x]
    p_safe = [s / sum(safe) for s in safe]
    assert all(abs(a - b) < 1e-12 for a, b in zip(p, p_safe))

    # online pass: running max and running denominator
    steps, mm, d = [], -math.inf, 0.0
    for v in x:
        m_new = max(mm, v)
        scale = math.exp(mm - m_new) if mm != -math.inf else 0.0
        d = d * scale + math.exp(v - m_new)
        steps.append({"x": v, "m_old": None if mm == -math.inf else mm, "m": m_new,
                      "rescaled": mm != -math.inf and m_new > mm,
                      "scale": r(scale, 4), "d": r(d, 4)})
        mm = m_new
    assert mm == m and abs(d - sum(safe)) < 1e-12

    # merge two halves computed separately
    def partial(xs):
        mx = max(xs)
        return mx, sum(math.exp(v - mx) for v in xs)
    m1, d1 = partial(x[:3])
    m2, d2 = partial(x[3:])
    mg = max(m1, m2)
    dg = d1 * math.exp(m1 - mg) + d2 * math.exp(m2 - mg)
    assert mg == m and abs(dg - d) < 1e-12

    OUT.write_text(json.dumps({
        "x": x, "n": n,
        "exp": [r(e, 2) for e in ex],
        "p": [r(v, 3) for v in p], "pct": [round(100 * v, 1) for v in p],
        "max": m, "safe": [r(s, 4) for s in safe], "d": r(d, 4), "d2": r(d, 2),
        "steps": steps,
        "rescales": [s for s in steps if s["rescaled"]],
        "fp16_max": int(fp16_max), "ln16": r(ln16, 2), "fp32_max_e": 38, "ln32": r(ln32, 2),
        "half": {"m1": m1, "d1": r(d1, 4), "m2": m2, "d2": r(d2, 4),
                 "scale1": r(math.exp(m1 - mg), 4), "d": r(dg, 4)},
        "sources_year": {"milakov": 2018, "flash": 2022},
    }, indent=2))


if __name__ == "__main__":
    main()
