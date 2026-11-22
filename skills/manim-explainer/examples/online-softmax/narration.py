"""Narration for 'Online softmax: one pass instead of two'. Numbers come from numbers.json.

Written in the plain mode of the owner's style guide (NARRATION_STYLE), and directed for
delivery (references/voice.md): each scene opens with a reset (a discourse marker, a question
or a lift), explains on a steady line with one stressed word per beat, and settles at the end.
[Bracketed tags] are performed by eleven_v4 and never spoken; script.md shows the words alone.
"""

import json
from pathlib import Path

N = json.loads(Path(__file__).with_name("numbers.json").read_text())
X = N["x"]
S = N["steps"]
H = N["half"]

TITLE = "Online softmax: one pass instead of two"
OUTPUT_NAME = "online_softmax.mp4"
VOICE_NAME = "will"
MODEL = "eleven_v4"
INTRO = f"Worked example: scores {X}. Every number comes from compute.py through numbers.json."
SOURCES = [
    "Maxim Milakov and Natalia Gimelshein, 'Online normalizer calculation for softmax', "
    "arXiv:1805.02867 (2018).",
    "Tri Dao, Daniel Y. Fu, Stefano Ermon, Atri Rudra and Christopher Re, 'FlashAttention: Fast "
    "and Memory-Efficient Exact Attention with IO-Awareness', NeurIPS 2022.",
    f"IEEE 754 half precision: largest finite value {N['fp16_max']:,}, so e to the x overflows "
    f"once x passes about {N['ln16']}.",
]

SCENES = [
    ("S01_Softmax", "What softmax does", [
        ("a1", "[warmly] Okay, so a neural network usually finishes each step with a list of raw "
               "scores, one for every option it could pick. Here are six of them."),
        ("a2", "They aren't probabilities yet, because a score can be any size, and it can even be "
               "negative. Softmax, which is the function that turns scores into probabilities, "
               "does it in two moves."),
        ("a3", "First, it raises e to the power of each score. Every value comes out positive... "
               "and the big scores pull WAY ahead of the small ones."),
        ("a4", "Then it divides each one by the total, so the bars add up to exactly one. "
               f"[amused] The score of {X[4]} ends up with {N['pct'][4]} percent of the weight."),
    ]),
    ("S02_Overflow", "Why we subtract the max", [
        ("b1", "[curious] Now, there's a catch, and it's hiding in that exponential. Watch how "
               "fast e to the x grows."),
        ("b2", "Models often run in half precision, in which the largest number you can store is "
               f"{N['fp16_max']:,}. That's e to the power of about {round(N['ln16'])}. [emphatic] "
               "So a score of just TWELVE already overflows, and the answer turns into infinity."),
        ("b3", f"[matter-of-fact] The fix is to slide every score down by the largest one, which "
               f"here is {N['max']}. Now the top score sits at zero, and nothing is above it. So e "
               "to any of them lands between zero and one."),
        ("b4", "[thoughtful] And the answer doesn't change. Subtracting the max multiplies the top "
               "and the bottom of the fraction by the same number, and that cancels out."),
    ]),
    ("S03_Passes", "The price: an extra pass", [
        ("c1", "[sighs] That safety has a cost, though. In a real model this list can hold a "
               "hundred thousand scores, and reading them from memory is the slow part."),
        ("c2", "The first pass walks the whole list... just to find the max."),
        ("c3", "The second pass walks it AGAIN, to add up e to each score minus the max."),
        ("c4", "And the third pass divides to get the probabilities. [curious] So why can't the "
               "first two passes be one? [thoughtful] Well, you'd need the max before you start "
               "adding, but you only know the max once you've seen everything."),
    ]),
    ("S04_Online", "Fix the sum as you go", [
        ("d1", "[excited] Here's the trick. You stop waiting for the max, and you keep two running "
               "numbers instead. One is the biggest score so far, which I'll call m. The other is "
               "a running total, which I'll call d, and it's always measured against the current "
               "m."),
        ("d2", f"The first score is {S[0]['x']}. It's the biggest so far, so it counts as e to the "
               "zero, which is one."),
        ("d3", f"Next comes {S[1]['x']}. That's below the max, so it adds e to the minus "
               f"{X[0] - X[1]}, which is only a sliver. The total is now {S[1]['d']:.2f}."),
        ("d4", f"[curious] Then {S[2]['x']} arrives, which is a new max. Everything in the total "
               f"was measured against {S[2]['m_old']}... and now the ruler has moved. So the whole "
               f"total shrinks by e to the minus {S[2]['m'] - S[2]['m_old']}, and then the new "
               "leader adds one."),
        ("d5", f"{S[3]['x']} is small, so it just adds a sliver. Then {S[4]['x']} sets a new "
               "record, and the same thing happens again. Everything shrinks together. Then the "
               "new leader adds one."),
        ("d6", f"Last comes {S[5]['x']}. That's one pass, and the total is {N['d']:.2f}. "
               "[amused] It's EXACTLY what the slow way gave us."),
    ]),
    ("S05_Why", "Why the shrink is exact", [
        ("e1", "[curious] So why is the shrink allowed? Each piece of the total is e to a score "
               "minus the old max."),
        ("e2", "Multiply it by e to the old max minus the new max. The exponents add up, the old "
               "max cancels out... and every piece is now measured against the new max, as if "
               "you'd known it all along."),
        ("e3", "[matter-of-fact] That leaves the whole algorithm in two lines. The new max is the "
               "bigger of the old max and the new score. The new total is the old total, "
               "rescaled, plus the new term."),
    ]),
    ("S06_Merge", "Splitting the work", [
        ("f1", "Okay. That takes us from three passes down to two. [excited] But the same rule "
               "does something more useful than that."),
        ("f2", "Split the list in half and give each half to a different worker. The left half "
               f"finishes with a max of {H['m1']}, and the right half finishes with a max of "
               f"{H['m2']}."),
        ("f3", "To combine them, you use the same move. The side with the smaller max shrinks, "
               f"and then the two totals add. You get {H['d']:.2f} again, which is the SAME "
               "number."),
        ("f4", "[thoughtful] This is what lets a GPU split one softmax across many threads. "
               "FlashAttention, which is a faster way to compute attention in transformers, takes "
               "it one step further. It keeps a running output next to the running total and "
               "rescales both, so it never has to store the full attention matrix."),
    ]),
    ("S07_Close", "The one move", [
        ("g1", "[warmly] So online softmax comes down to one move. When the max goes up, "
               "everything you've added so far shrinks by e to the old max minus the new max... "
               "and then you carry on."),
        ("g2", "[softly] That one move keeps the numbers from overflowing, it turns two passes "
               "into one, and it lets you split the work and put it back together exactly."),
    ]),
]

BEAT_TEXT = {bid: text for _, _, beats, *_ in SCENES for bid, text in beats}
