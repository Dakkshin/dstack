"""Every number shown or spoken is computed here and written to numbers.json.

This is a starter, not a topic. Replace the body of main() with the numbers your
video needs, and keep one assert per fact so a wrong value fails the build.
"""

import json
from pathlib import Path

OUT = Path(__file__).with_name("numbers.json")


def main():
    n = 6
    pairs = n * (n - 1) // 2
    assert pairs == sum(range(n))

    OUT.write_text(json.dumps({"n": n, "pairs": pairs}, indent=2))


if __name__ == "__main__":
    main()
