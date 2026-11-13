#!/usr/bin/env python3
"""Build a full-page Excalidraw mindmap from a JSON tree.

    python3 build.py map.json out.html          # build
    python3 build.py map.json --check           # validate only

The JSON shape is documented in ../SKILL.md. Exit code 1 means an error the
page cannot survive (missing fields, too deep); warnings print but still build.
"""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
TEMPLATE = HERE.parent / "assets" / "template.html"

MAX_DEPTH = 4            # root=0 .. 4; beyond this the canvas gets unreadable
TITLE_WARN = 34          # cards are nowrap; longer titles crowd the next column
TITLE_MAX = 44
DESC_WARN = 180          # the drawer is one line-ish; long desc reads as a wall
PILLARS = (3, 8)
CHILDREN_WARN = 7


def validate(m):
    errors, warnings = [], []
    if not isinstance(m, dict):
        return ["top level must be an object"], warnings
    if not m.get("title"):
        errors.append("missing top-level 'title'")
    root = m.get("root")
    if not isinstance(root, dict):
        errors.append("missing 'root' object")
        return errors, warnings

    def walk(node, depth, path):
        where = path or "root"
        title = node.get("title")
        if not isinstance(title, str) or not title.strip():
            errors.append(f"{where}: missing 'title'")
            title = ""
        elif len(title) > TITLE_MAX:
            errors.append(f"{where}: title is {len(title)} chars (max {TITLE_MAX}): {title!r}")
        elif len(title) > TITLE_WARN and depth > 0:
            warnings.append(f"{where}: title is {len(title)} chars, aim for <= {TITLE_WARN}: {title!r}")
        if not node.get("desc"):
            warnings.append(f"{where}: no 'desc', the drawer will be empty for {title!r}")
        elif len(node["desc"]) > DESC_WARN:
            warnings.append(f"{where}: desc is {len(node['desc'])} chars, aim for <= {DESC_WARN}")
        kids = node.get("children") or []
        if not isinstance(kids, list):
            errors.append(f"{where}: 'children' must be a list")
            return
        if depth == 0 and not (PILLARS[0] <= len(kids) <= PILLARS[1]):
            warnings.append(f"root has {len(kids)} pillars, aim for {PILLARS[0]}-{PILLARS[1]}")
        if depth > 0 and len(kids) > CHILDREN_WARN:
            warnings.append(f"{where}: {len(kids)} children, split it (aim for <= {CHILDREN_WARN})")
        if kids and depth >= MAX_DEPTH:
            errors.append(f"{where}: deeper than {MAX_DEPTH} levels, flatten it")
            return
        for i, c in enumerate(kids):
            walk(c, depth + 1, f"{where}.{i}")

    walk(root, 0, "")
    return errors, warnings


def prepare(m):
    """Assign stable ids and the default open state."""
    root = m["root"]
    root["id"] = "root"
    root["expanded"] = True
    open_pillars = int(m.get("openPillars", 2))

    def walk(node, depth, idx, path):
        if depth > 0:
            node["id"] = path
            if "expanded" not in node and node.get("children"):
                node["expanded"] = depth == 1 and idx < open_pillars
        for i, c in enumerate(node.get("children") or []):
            walk(c, depth + 1, i, f"{path}_{i}")

    walk(root, 0, 0, "n")
    return m


def build(m):
    html = TEMPLATE.read_text(encoding="utf-8")
    # "</" inside a <script> would end it early; JSON allows the escaped form
    data = json.dumps(m, ensure_ascii=False).replace("</", "<\\/")
    title = m["title"] if not m.get("unit") else f"{m['unit']} {m['title']}"
    title = title.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    for slot in ("/*__MINDMAP_DATA__*/null", "__MINDMAP_TITLE__"):
        if html.count(slot) != 1:
            sys.exit(f"template is missing slot {slot}")
    return html.replace("/*__MINDMAP_DATA__*/null", data).replace("__MINDMAP_TITLE__", title)


def count(node):
    return 1 + sum(count(c) for c in node.get("children") or [])


def main(argv):
    if len(argv) < 2 or (len(argv) < 3 and "--check" not in argv):
        sys.exit(__doc__)
    src = Path(argv[1])
    m = json.loads(src.read_text(encoding="utf-8"))
    errors, warnings = validate(m)
    for w in warnings:
        print("warn:", w)
    for e in errors:
        print("ERROR:", e)
    if errors:
        sys.exit(1)
    nodes = count(m["root"])
    if "--check" in argv:
        print(f"ok: {nodes} nodes, {len(m['root'].get('children') or [])} pillars")
        return
    out = Path(argv[2])
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(build(prepare(m)), encoding="utf-8")
    print(f"built {out} ({nodes} nodes, {len(warnings)} warnings)")


if __name__ == "__main__":
    main(sys.argv)
