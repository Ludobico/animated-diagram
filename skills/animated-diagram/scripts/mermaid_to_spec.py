#!/usr/bin/env python3
"""Convert a Mermaid flowchart into the JSON spec used by make_diagram.py.

    python mermaid_to_spec.py diagram.mmd spec.json     (or '-' to read stdin)

Handles: subgraph blocks (innermost subgraph becomes the group), node shapes
[] () ([]) [()] (()) {{}} {} >], quoted labels, <br/> label/sub-label split,
-->, ---, -.->, ==>, |text| and -- text --> edge labels, chains (A --> B --> C)
and A & B --> C. Style/class/click lines and %% comments are ignored.
"""
import json
import re
import sys
from pathlib import Path

OPENERS = [("[(", ")]", "cylinder"), ("([", "])", None), ("((", "))", None), ("{{", "}}", None),
           ("[[", "]]", None), ("[", "]", None), ("(", ")", None), ("{", "}", None), (">", "]", None)]
LABELED = re.compile(r"(--|==|-\.)\s+(.+?)\s+(-->|==>|\.->|---|===|\.-)")
PLAIN = re.compile(r"(-->|==>|-\.->|---|===|-\.-)(?:\s*\|([^|]*)\|)?")
# `%%` sits outside the \b group: "%% note" has no word boundary after the second %
IGNORE = re.compile(r"^(?:%%|(?:flowchart|graph|classDef|class|style|linkStyle|click|direction)\b)", re.I)


def clean_label(raw):
    raw = raw.strip()
    if len(raw) >= 2 and raw[0] == raw[-1] == '"':
        raw = raw[1:-1]
    parts = [p.strip() for p in re.split(r"<br\s*/?>|\\n", raw) if p.strip()]
    parts = [re.sub(r"<[^>]+>", "", p) for p in parts]
    return (parts[0] if parts else raw), (" ".join(parts[1:]) or None)


def parse_node(s, i):
    m = re.compile(r"[^\s\[\](){}>&|\-=.]+(?:[-.][^\s\[\](){}>&|\-=.]+)*").match(s, i)
    if not m:
        return None, i
    nid, i = m.group(0), m.end()
    info = {"id": nid}
    for op, cl, shape in OPENERS:
        if s.startswith(op, i):
            j = s.find(cl, i + len(op))
            if j < 0:
                break
            label, sub = clean_label(s[i + len(op):j])
            info.update(label=label)
            if sub:
                info["sub"] = sub
            if shape:
                info["shape"] = shape
            i = j + len(cl)
            break
    m2 = re.compile(r":::\w+").match(s, i)
    if m2:
        i = m2.end()
    return info, i


def parse_nodelist(s, i):
    nodes = []
    while True:
        i = len(s) - len(s[i:].lstrip())
        node, i = parse_node(s, i)
        if node is None:
            return nodes, i
        nodes.append(node)
        j = len(s) - len(s[i:].lstrip())
        if s.startswith("&", j):
            i = j + 1
            continue
        return nodes, i


def parse_link(s, i):
    i = len(s) - len(s[i:].lstrip())
    m = LABELED.match(s, i)
    if m:
        return m.group(2), m.end()
    m = PLAIN.match(s, i)
    if m:
        return (m.group(2) or "").strip() or None, m.end()
    return False, i


def convert(text):
    groups, nodes, edges = [], {}, []
    stack = []

    def ensure_group(gid, title):
        if gid not in [g["id"] for g in groups]:
            groups.append({"id": gid, "title": title})

    def touch(info):
        cur = nodes.get(info["id"])
        if cur is None:
            cur = {"id": info["id"], "label": info.get("label", info["id"])}
            nodes[info["id"]] = cur
        for k in ("label", "sub", "shape"):
            if k in info:
                cur[k] = info[k]
        if stack and "group" not in cur:
            cur["group"] = stack[-1]
        return cur["id"]

    for raw in text.splitlines():
        line = raw.strip().rstrip(";")
        if not line or IGNORE.match(line):
            continue
        m = re.match(r"subgraph\s+(.+)$", line, re.I)
        if m:
            rest = m.group(1).strip()
            mm = re.match(r"([^\s\[]+)\s*\[(.*)\]$", rest)
            gid, title = (mm.group(1), clean_label(mm.group(2))[0]) if mm else (re.sub(r"\W+", "_", rest), rest.strip('"'))
            ensure_group(gid, title)
            stack.append(gid)
            continue
        if line.lower() == "end":
            if stack:
                stack.pop()
            continue
        lefts, i = parse_nodelist(line, 0)
        if not lefts:
            continue
        ids_left = [touch(x) for x in lefts]
        while True:
            label, j = parse_link(line, i)
            if label is False:
                break
            rights, i = parse_nodelist(line, j)
            if not rights:
                break
            ids_right = [touch(x) for x in rights]
            for a in ids_left:
                for b in ids_right:
                    e = {"from": a, "to": b}
                    if label:
                        e["label"] = label
                    edges.append(e)
            ids_left = ids_right

    for nd in nodes.values():
        if "group" not in nd:
            ensure_group("main", "")
            nd["group"] = "main"
    return {"optimize_order": True, "groups": groups, "nodes": list(nodes.values()), "edges": edges}


if __name__ == "__main__":
    if len(sys.argv) < 3:
        raise SystemExit("usage: mermaid_to_spec.py diagram.mmd spec.json")
    src = sys.stdin.read() if sys.argv[1] == "-" else Path(sys.argv[1]).read_text(encoding="utf-8")
    src = re.sub(r"^\s*```(?:mermaid)?\s*$", "", src, flags=re.M)
    if re.search(r"^\s*(flowchart|graph)\s+(TD|TB|BT)\b", src, re.M | re.I):
        print("warning: top-down diagram; layout is always left-to-right columns by group", file=sys.stderr)
    spec = convert(src)
    Path(sys.argv[2]).write_text(json.dumps(spec, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"wrote {sys.argv[2]}: {len(spec['groups'])} groups, {len(spec['nodes'])} nodes, {len(spec['edges'])} edges")
