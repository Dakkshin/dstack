"""Narration, split into beats. Each beat is one TTS clip and one block of animation.

Every number spoken is read from numbers.json, so the voice and the screen agree.
Replace the placeholder topic. Keep the shape.
"""

import json
from pathlib import Path

N = json.loads(Path(__file__).with_name("numbers.json").read_text())

TITLE = "<Topic>: narration script"
OUTPUT_NAME = "explainer.mp4"
VOICE_NAME = ""  # ask the person: mark, alex, will or matilda (jessica on request)
INTRO = "Every number below comes from compute.py through numbers.json."
SOURCES: list[str] = []

SCENES: list[tuple[str, str, list[tuple[str, str]]]] = [
    ("S01_Hook", "Hook", [
        ("h1", "Here is the question this video answers."),
        ("h2", f"Take {N['n']} people in a room, where every pair shakes hands once."),
    ]),
    ("S02_Idea", "The idea", [
        ("i1", f"Each person shakes {N['n'] - 1} hands, but that counts every handshake twice."),
        ("i2", f"So the room makes {N['pairs']} handshakes in all."),
    ]),
]

BEAT_TEXT = {bid: text for _, _, beats in SCENES for bid, text in beats}
