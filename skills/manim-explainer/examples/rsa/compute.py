"""Every number shown in the video is computed here and written to numbers.json.

The scenes read numbers.json and never hardcode a value, so the video cannot show a
number that Python did not produce. Run: python compute.py
"""

import hashlib
import json
import math
import random
from pathlib import Path

OUT = Path(__file__).with_name("numbers.json")


def is_probable_prime(n: int, rounds: int = 40, rng: random.Random | None = None) -> bool:
    if n < 2:
        return False
    for sp in (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37):
        if n % sp == 0:
            return n == sp
    rng = rng or random.Random(0)
    d, s = n - 1, 0
    while d % 2 == 0:
        d //= 2
        s += 1
    for _ in range(rounds):
        a = rng.randrange(2, n - 1)
        x = pow(a, d, n)
        if x in (1, n - 1):
            continue
        for _ in range(s - 1):
            x = pow(x, 2, n)
            if x == n - 1:
                break
        else:
            return False
    return True


def random_prime(bits: int, rng: random.Random) -> int:
    while True:
        c = rng.getrandbits(bits) | (1 << (bits - 1)) | (1 << (bits - 2)) | 1
        if is_probable_prime(c, rng=rng):
            return c


def egcd_table(a: int, b: int):
    """Extended Euclid on (a, b) as rows of (r, q, s, t) with r = s*a + t*b."""
    rows: list[tuple[int, int | None, int, int]] = [(a, None, 1, 0), (b, None, 0, 1)]
    while rows[-1][0] != 0:
        (r0, _, s0, t0), (r1, _, s1, t1) = rows[-2], rows[-1]
        q = r0 // r1
        rows[-1] = (r1, q, s1, t1)
        rows.append((r0 - q * r1, None, s0 - q * s1, t0 - q * t1))
    return rows


def euclid_divisions(a: int, b: int):
    steps = []
    while b:
        q, r = divmod(a, b)
        steps.append({"a": a, "b": b, "q": q, "r": r})
        a, b = b, r
    return steps


def back_substitute(divs):
    """Express 1 (the last nonzero remainder) as x*A + y*B, walking back up the divisions.

    Each row is (x, A, y, B) meaning 1 = x*A + y*B."""
    j = max(i for i, dv in enumerate(divs) if dv["r"] != 0)
    assert divs[j]["r"] == 1
    x, A, y, B = 1, divs[j]["a"], -divs[j]["q"], divs[j]["b"]
    rows = [(x, A, y, B)]
    for i in range(j - 1, -1, -1):
        dv = divs[i]
        assert B == dv["r"] and A == dv["b"]
        x, A, y, B = y, dv["a"], x - y * dv["q"], dv["b"]
        assert x * A + y * B == 1
        rows.append((x, A, y, B))
    return rows


def square_and_multiply(base: int, exp: int, mod: int):
    """Left-to-right binary exponentiation; returns the step trace."""
    bits = bin(exp)[2:]
    acc = 1
    trace = []
    for i, bit in enumerate(bits):
        if i > 0:
            acc = acc * acc % mod
            trace.append({"op": "S", "bit_index": i, "value": acc})
        if bit == "1":
            acc = acc * base % mod if i > 0 else base % mod
            trace.append({"op": "M" if i > 0 else "init", "bit_index": i, "value": acc})
    assert acc == pow(base, exp, mod)
    return bits, trace


def icbrt(x: int) -> int:
    lo, hi = 0, 1 << ((x.bit_length() + 2) // 3 + 1)
    while lo < hi:
        mid = (lo + hi + 1) // 2
        if mid**3 <= x:
            lo = mid
        else:
            hi = mid - 1
    return lo


def main():
    p, q = 61, 53
    assert is_probable_prime(p) and is_probable_prime(q)
    n = p * q
    phi = (p - 1) * (q - 1)
    e = 17
    assert math.gcd(e, phi) == 1
    d = pow(e, -1, phi)
    k = (e * d - 1) // phi
    assert e * d == 1 + k * phi

    table = egcd_table(phi, e)
    # last nonzero remainder row holds the Bezout coefficients
    gcd_row = [r for r in table if r[0] != 0][-1]
    assert gcd_row[0] == 1
    t_raw = gcd_row[3]
    assert t_raw % phi == d

    m = 65
    c = pow(m, e, n)
    m_back = pow(c, d, n)
    assert m_back == m

    enc_bits, enc_trace = square_and_multiply(m, e, n)
    dec_bits, dec_trace = square_and_multiply(c, d, n)

    # CRT decryption
    dp, dq, qinv = d % (p - 1), d % (q - 1), pow(q, -1, p)
    m1, m2 = pow(c, dp, p), pow(c, dq, q)
    h = (qinv * (m1 - m2)) % p
    m_crt = m2 + h * q
    assert m_crt == m

    # trial division of the toy modulus
    trial = []
    for cand in range(2, math.isqrt(n) + 1):
        trial.append(cand)
        if n % cand == 0:
            break
    found = trial[-1]
    assert found == q

    # a real 2048-bit modulus (deterministic seed so renders are reproducible)
    rng = random.Random(2108)
    P = random_prime(1024, rng)
    Q = random_prime(1024, rng)
    while Q == P:
        Q = random_prime(1024, rng)
    N = P * Q
    assert N.bit_length() == 2048
    N_digits = len(str(N))
    sqrtN_digits = len(str(math.isqrt(N)))
    primes_below_sqrt_order = math.isqrt(N).bit_length()  # ~2^1024 candidates

    # e = 65537 cost vs toy e
    F4 = 65537
    f4_bits = bin(F4)[2:]
    # e=3 with no padding: m^3 < N means c is m^3 over the integers
    secret = int.from_bytes(b"PIN 4821", "big")
    c3 = pow(secret, 3, N)
    assert secret**3 < N and c3 == secret**3
    recovered = icbrt(c3)
    assert recovered == secret

    # determinism: a guessing attacker re-encrypts candidates
    yes, no = int.from_bytes(b"YES", "big"), int.from_bytes(b"NO", "big")
    c_yes, c_no = pow(yes, F4, N), pow(no, F4, N)

    # toy signature: hash reduced mod n (illustrative only, real RSA signs a padded hash)
    msg = "CSI2108"
    hm = int.from_bytes(hashlib.sha256(msg.encode()).digest(), "big") % n
    sig = pow(hm, d, n)
    assert pow(sig, e, n) == hm

    # timing: per-bit work of d (square always, multiply on 1-bits)
    d_bits = bin(d)[2:]

    divs = euclid_divisions(phi, e)
    backsub = back_substitute(divs)
    assert backsub[-1][1] == phi and backsub[-1][3] == e and backsub[-1][2] % phi == d
    # first squaring shown in full: 65^2 = qn + r
    sq = m * m
    people = 1000

    data = {
        "backsub": [list(r) for r in backsub],
        "m_sq": sq, "m_sq_q": sq // n, "m_sq_r": sq % n,
        "people": people, "pair_keys": people * (people - 1) // 2,
        "naive_mults_d": d - 1,
        "rsa250_bits": 829, "rsa250_digits": 250, "rsa250_core_years": 2700, "rsa250_year": 2020,
        "p": p, "q": q, "n": n, "phi": phi, "e": e, "d": d, "k": k, "ed": e * d,
        "egcd_divisions": euclid_divisions(phi, e),
        "egcd_table": [{"r": r, "q": qq, "s": s, "t": t} for r, qq, s, t in table],
        "egcd_t_raw": t_raw,
        "m": m, "c": c, "m_back": m_back,
        "enc_bits": enc_bits, "enc_trace": enc_trace,
        "dec_bits": dec_bits,
        "dec_squarings": sum(1 for s in dec_trace if s["op"] == "S"),
        "dec_mults": sum(1 for s in dec_trace if s["op"] == "M"),
        "enc_squarings": sum(1 for s in enc_trace if s["op"] == "S"),
        "enc_mults": sum(1 for s in enc_trace if s["op"] == "M"),
        "dp": dp, "dq": dq, "qinv": qinv, "m1": m1, "m2": m2, "h": h,
        "trial_count": len(trial), "trial_found": found, "sqrt_n": math.isqrt(n),
        "N": str(N), "N_bits": N.bit_length(), "N_digits": N_digits,
        "sqrtN_digits": sqrtN_digits, "sqrtN_bits": primes_below_sqrt_order,
        "F4": F4, "f4_bits": f4_bits, "f4_squarings": len(f4_bits) - 1,
        "f4_mults": f4_bits.count("1") - 1,
        "naive_mults_2048": 2**2048 > 0 and "2^2048",
        "sm_ops_2048_max": 2 * 2048,
        "e3_secret_text": "PIN 4821", "e3_secret": str(secret), "e3_c": str(c3),
        "e3_secret_bits": secret.bit_length(), "e3_c_bits": c3.bit_length(),
        "e3_recovered": str(recovered),
        "c_yes_head": str(c_yes)[:24], "c_no_head": str(c_no)[:24],
        "sig_msg": msg, "sig_hash_mod_n": hm, "sig": sig, "sig_check": pow(sig, e, n),
        "d_bits": d_bits, "d_bit_count": len(d_bits), "d_popcount": d_bits.count("1"),
    }
    OUT.write_text(json.dumps(data, indent=2))
    print(f"wrote {OUT.name}: n={n} phi={phi} d={d} c={c} k={k} N_digits={N_digits}")


if __name__ == "__main__":
    main()
