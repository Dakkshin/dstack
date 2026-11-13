"""Narration, split into beats. Each beat is one TTS clip and one block of animation.

Every number spoken comes from numbers.json, so the voice and the screen cannot disagree.
Historical facts (dates, records) are fixed values in compute.py, cited in SOURCES.
"""

import json
from pathlib import Path

N = json.loads(Path(__file__).with_name("numbers.json").read_text())
bs = N["backsub"][-1]

TITLE = "RSA explainer: narration script"
OUTPUT_NAME = "rsa_explainer.mp4"
INTRO = (
    "CSI2108 Cryptographic Concepts viva prep. Every number below was computed by `compute.py` "
    "and is read from `numbers.json` by both the narration and the scenes.\n\n## Toy key\n\n"
    f"p = {N['p']}, q = {N['q']}, n = {N['n']}, φ(n) = {N['phi']}, e = {N['e']}, d = {N['d']} "
    f"(check: e·d = {N['ed']} = 1 + {N['k']}·φ(n)). m = {N['m']} encrypts to c = {N['c']} "
    f"and decrypts back to {N['m_back']}."
)
SOURCES = [
    "Rivest, Shamir, Adleman, 'A Method for Obtaining Digital Signatures and Public-Key "
    "Cryptosystems', MIT memo 1977, CACM 1978.",
    "RSA-250 (829 bits) factored Feb 2020 by Boudot, Gaudry, Guillevic, Heninger, Thomé and "
    "Zimmermann: about 2,700 core-years (Intel Xeon Gold 6130 at 2.1 GHz).",
    "NIST SP 800-57 Part 1 Rev. 5: 2048-bit RSA gives 112 bits of security.",
    "P. Kocher, 'Timing Attacks on Implementations of Diffie-Hellman, RSA, DSS, and Other "
    "Systems', CRYPTO 1996.",
    "D. Bleichenbacher, 'Chosen Ciphertext Attacks Against Protocols Based on the RSA Encryption "
    "Standard PKCS #1', CRYPTO 1998. ROBOT (Böck, Somorovsky, Young), 2017.",
    "RFC 8446 (TLS 1.3): static RSA key exchange removed; RSA signatures use RSASSA-PSS.",
    "RFC 8017 (PKCS #1 v2.2): RSAES-OAEP and RSASSA-PSS. FIPS 203: ML-KEM.",
]

SCENES: list[tuple[str, str, list[tuple[str, str]]]] = [
    ("S01_Hook", "Hook", [
        ("h1", "How can anyone lock a box that only one person can open?"),
        ("h2", "Picture a padlock you hand out for free. Anyone can snap it shut on a box. "
               "Only you hold the key that opens it."),
        ("h3", "That is the promise of RSA, published by Rivest, Shamir and Adleman in 1977. "
               "Let's build it with numbers small enough to check by hand."),
    ]),
    ("S02_Problem", "The problem", [
        ("p1", "Start with symmetric encryption, like AES. One key locks, and the same key unlocks."),
        ("p2", "It is fast, but before Alice and Bob can talk in secret, they already need a shared secret. "
               "Send the key over the network, and Eve simply copies it."),
        ("p3", f"It also scales badly. With {N['people']} people, every pair needs its own key, "
               f"which is {N['pair_keys']:,} keys."),
        ("p4", "What we want instead is two different keys. A public key that only locks, "
               "and a private key that only unlocks."),
    ]),
    ("S03_Trapdoor", "The idea", [
        ("i1", "The trick is a trapdoor one way function. It is easy to compute forwards, "
               "and hard to reverse, unless you know a secret."),
        ("i2", f"Multiplying primes is easy. {N['p']} times {N['q']} is {N['n']}, done in a blink."),
        ("i3", f"Going backwards, from {N['n']} to its factors, means searching. "
               "For numbers hundreds of digits long, nobody knows a fast way."),
        ("i4", "The primes are the trapdoor. Whoever knows them can undo the lock. "
               "Everyone else is stuck."),
    ]),
    ("S04_KeyGen", "Key generation", [
        ("k1", f"Here is key generation. Pick two primes. p equals {N['p']}, and q equals {N['q']}."),
        ("k2", f"Multiply them to get the modulus n, which is {N['n']}. This number is public."),
        ("k3", f"Next, phi of n, which is p minus one, times q minus one. That is {N['phi']}. "
               "It counts the numbers below n that share no factor with n, and it must stay secret."),
        ("k4", f"Choose a public exponent e that shares no factor with phi. We will take e equals {N['e']}."),
        ("k5", f"The private exponent d is the inverse of e, mod phi. We need {N['e']} times d "
               f"to leave a remainder of one when divided by {N['phi']}. "
               "The extended Euclidean algorithm finds it."),
        ("k6", "Run Euclid's algorithm first. "
               + " ".join(f"{dv['a']} divided by {dv['b']} gives {dv['q']}, remainder {dv['r']}."
                          for dv in N["egcd_divisions"] if dv["r"] != 0)
               + " The remainder reached one, so an inverse exists."),
        ("k7", "Now walk back up, writing each remainder in terms of the two before it. "
               f"The last line says one equals {bs[0]} times {bs[1]}, "
               f"minus {-bs[2]} times {bs[3]}."),
        ("k8", f"So minus {-bs[2]} is an inverse of {N['e']}. Add {N['phi']} to make it positive, "
               f"and d equals {N['d']}. The public key is n and e. The private key is d."),
    ]),
    ("S05_EncryptDecrypt", "Encrypt and decrypt", [
        ("c1", f"To encrypt a message m, here {N['m']}, raise it to the power e, and reduce mod n."),
        ("c2", f"Mod n is clock arithmetic. Picture a clock with {N['n']} positions. "
               "Pass the top and you wrap back to zero. Only where you land matters."),
        ("c3", f"{N['m']} squared is {N['m_sq']}, which wraps once and lands on {N['m_sq_r']}. "
               + "Square again, " + ". Again, ".join(str(s["value"]) for s in N["enc_trace"][2:-1])
               + f". That is {N['m']} to the sixteenth. "
               f"One more multiply by {N['m']} lands on {N['c']}."),
        ("c4", f"The ciphertext c is {N['c']}. It looks nothing like {N['m']}."),
        ("c5", f"To decrypt, raise c to the power d, {N['d']}, mod n. "
               f"The hand wraps around the clock again and again, and lands exactly on {N['m_back']}."),
    ]),
    ("S06_WhyItWorks", "Why it works", [
        ("w1", "Why does raising to d undo raising to e? Because e times d is one more than "
               f"a multiple of phi. Here {N['e']} times {N['d']} is {N['ed']}, "
               f"which is one plus {N['k']} times {N['phi']}."),
        ("w2", "So c to the d is m to the e d, which is m to the one plus k phi. "
               "Split that into m, times m to the phi, all raised to the k."),
        ("w3", "Euler's theorem says that if m shares no factor with n, "
               "then m to the phi of n is one, mod n."),
        ("w4", "So the bracket collapses to one, and we are left with m. Decryption returns the message."),
        ("w5", "A detail most people miss. It still works when m does share a factor with n. "
               "Check the congruence mod p and mod q separately with Fermat's little theorem, "
               "then join them with the Chinese remainder theorem."),
    ]),
    ("S07_Security", "Why it is secure", [
        ("s1", "An attacker sees n and e. To get d they need phi, and to get phi they need "
               "p and q. So they try to factor n."),
        ("s2", f"For {N['n']}, trial division finds {N['trial_found']} after testing "
               f"{N['trial_count']} candidates. Instant."),
        ("s3", f"Real RSA uses a {N['N_bits']} bit modulus. This is one, {N['N_digits']} digits long."),
        ("s4", f"Trial division would have to search up to its square root, a {N['sqrtN_digits']} digit number. "
               f"The general number field sieve is far faster, yet the public record is a {N['rsa250_digits']} digit number, "
               f"{N['rsa250_bits']} bits, factored in {N['rsa250_year']} "
               f"with about {N['rsa250_core_years']:,} CPU core years."),
        ("s5", f"{N['N_bits']} bit RSA is rated at about 112 bits of security. The real threat is a large "
               "quantum computer running Shor's algorithm, which is why post quantum schemes "
               "like ML-KEM are being deployed now."),
    ]),
    ("S08_Efficiency", "Efficiency", [
        ("f1", f"Computing c to the {N['d']} by multiplying {N['naive_mults_d']} times would be "
               f"hopeless at {N['N_bits']} bits. Square and multiply reads the exponent in binary instead."),
        ("f2", f"{N['d']} has {N['d_bit_count']} bits. Square at every bit after the first, "
               "and multiply when the bit is a one. "
               f"That is {N['dec_squarings']} squarings and {N['dec_mults']} multiplies, "
               f"instead of {N['naive_mults_d']} multiplications."),
        ("f3", f"For the public exponent, almost everyone uses {N['F4']}. In binary it is a one, "
               f"{len(N['f4_bits']) - 2} zeros, and a one. So encryption and verification cost just "
               f"{N['f4_squarings']} squarings and one multiply."),
        ("f4", "Decryption is the heavy side, so real implementations use the Chinese remainder theorem. "
               "Two half size exponentiations, mod p and mod q, roughly four times faster."),
        ("f5", "Even so, RSA is orders of magnitude slower than AES. So RSA only protects a symmetric key or signs a hash, and AES does the bulk work."),
    ]),
    ("S09_Breaks", "Where it breaks", [
        ("x1", "Everything so far is textbook RSA. And textbook RSA is not secure."),
        ("x2", "First, it is deterministic. The same message always gives the same ciphertext. "
               "If the answer is yes or no, the attacker encrypts both with your public key, and compares."),
        ("x3", "Second, a small e with no padding. With e equal to three and a short message, "
               "m cubed never even reaches n, so nothing wraps. "
               "The attacker takes an ordinary cube root, and reads the message."),
        ("x4", "Third, timing. Square and multiply does extra work on every one bit of d. "
               "Time enough decryptions and the key leaks, as Kocher showed in 1996. "
               "The fix is constant time code, and blinding."),
        ("x5", "The fix for the first two is padding. OAEP mixes the message with a fresh random seed "
               "before encrypting, so the same message encrypts differently every time."),
        ("x6", "And the older PKCS one, version one point five padding leaks through its error messages. "
               "Bleichenbacher's attack from 1998 came back in 2017 as ROBOT."),
    ]),
    ("S10_RealWorld", "Real world", [
        ("r1", "A signature runs RSA the other way round. Hash the message, raise the hash to d to sign, "
               "and anyone can raise the signature to e to check it."),
        ("r2", f"With our toy key, the hash of {N['sig_msg']}, reduced mod n, is {N['sig_hash_mod_n']}. "
               f"The signature is {N['sig']}. And {N['sig']} to the {N['e']}, mod {N['n']}, "
               f"gives back {N['sig_check']}. Verified."),
        ("r3", "That is what a TLS certificate is. A certificate authority signs the link between "
               "a domain name and its public key, and your browser checks that chain "
               "up to a root it already trusts."),
        ("r4", "And a detail examiners like. TLS 1.3 removed RSA key transport completely. "
               "The session key comes from ephemeral Diffie Hellman, for forward secrecy, "
               "and RSA only signs the handshake, using PSS padding."),
        ("r5", "Code signing is the same idea. Windows Authenticode, Linux package managers "
               "and secure boot all check a signature before running anything."),
    ]),
    ("S11_Recap", "Recap", [
        ("z1", "So here is the whole answer, in five lines."),
        ("z2", "Keys. n is p times q. e is public. d is the inverse of e, mod phi of n."),
        ("z3", "Encrypt with c equals m to the e. Decrypt with m equals c to the d. Both mod n."),
        ("z4", "It works because e d is one mod phi, so Euler's theorem gives m back."),
        ("z5", f"It is secure because finding d means factoring n, which is infeasible at {N['N_bits']} bits."),
        ("z6", "And in practice, it is always padded with OAEP or PSS, runs in constant time, "
               "and is used for keys and signatures, never bulk data."),
        ("z7", "A lock anyone can close, and a key only one person holds. That is RSA."),
    ]),
]

BEAT_TEXT = {bid: text for _, _, beats in SCENES for bid, text in beats}
