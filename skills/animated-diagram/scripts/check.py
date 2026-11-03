"""Check an SVG made by make_diagram.py before it is captured to GIF.

    python check.py out.svg [--loop 6]

Fails (exit 1) on:
  xml          the file does not parse or has no viewBox
  ids          duplicate id (clipPaths of a repeated icon would collide)
  canvas       a node, label or edge leaves the viewBox
  edge_node    an edge passes through a node it does not connect
  label        node labels / edge labels overlap each other or a node
  loop         a repeating animation's period does not divide the loop, or it has a positive begin
  icon         a node's icon has no micro-interaction of its own, or uses a colour outside the theme's
               palettes (a hard-coded #fff shows as a white patch in the dark theme)
Warns on:
  label_edge   an unrelated edge runs under an edge label, so it is unclear which line the label names
               (the reverse edge of an A->B / B->A pair is exempt: its port gap is always below the label height)
  crossing     two edges cross (some topologies cannot avoid it, e.g. 2 sources x 2 targets)

Geometry follows the layout make_diagram.py emits (data-graph-role, translate() on nodes,
M/L/C edge paths). Text size is estimated, not measured.
"""
import argparse
import math
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

from make_diagram import THEMES, text_width

NS = "{http://www.w3.org/2000/svg}"
NUM = r"-?\d+(?:\.\d+)?"


def tag(el):
    return el.tag.replace(NS, "")


def seconds(v):
    return float(v.rstrip("s")) if v else 0.0


def sample(d, steps=24):
    """Points along an M/L/C path."""
    tokens = re.findall(rf"[MLC]|{NUM}", d)
    pts, cmd, nums = [], None, []
    for t in tokens + ["M"]:
        if t in "MLC":
            if cmd in ("M", "L"):
                pts.append((nums[0], nums[1]))
            elif cmd == "C":
                (x0, y0), (x1, y1, x2, y2, x3, y3) = pts[-1], nums[:6]
                for i in range(1, steps + 1):
                    u = i / steps
                    a, b, c, e = (1 - u) ** 3, 3 * u * (1 - u) ** 2, 3 * u * u * (1 - u), u ** 3
                    pts.append((a * x0 + b * x1 + c * x2 + e * x3, a * y0 + b * y1 + c * y2 + e * y3))
            cmd, nums = t, []
        else:
            nums.append(float(t))
    return pts


def seg_hits_box(p, q, box, pad=0.0):
    """Liang-Barsky clip of segment p-q against an axis-aligned box."""
    l, t, r, b = box[0] - pad, box[1] - pad, box[2] + pad, box[3] + pad
    lo, hi = 0.0, 1.0
    dx, dy = q[0] - p[0], q[1] - p[1]
    for den, num in ((-dx, p[0] - l), (dx, r - p[0]), (-dy, p[1] - t), (dy, b - p[1])):
        if den == 0:
            if num < 0:
                return False
        else:
            u = num / den
            if den < 0:
                lo = max(lo, u)
            else:
                hi = min(hi, u)
            if lo > hi:
                return False
    return True


def boxes_overlap(a, b):
    return a[0] < b[2] and b[0] < a[2] and a[1] < b[3] and b[1] < a[3]


def seg_cross(p1, p2, p3, p4):
    d = (p2[0] - p1[0]) * (p4[1] - p3[1]) - (p2[1] - p1[1]) * (p4[0] - p3[0])
    if abs(d) < 1e-9:
        return None
    u = ((p3[0] - p1[0]) * (p4[1] - p3[1]) - (p3[1] - p1[1]) * (p4[0] - p3[0])) / d
    v = ((p3[0] - p1[0]) * (p2[1] - p1[1]) - (p3[1] - p1[1]) * (p2[0] - p1[0])) / d
    return (p1[0] + u * (p2[0] - p1[0]), p1[1] + u * (p2[1] - p1[1])) if 0 < u < 1 and 0 < v < 1 else None


def check(path, loop=6.0):
    fails, warns = {}, {}

    def fail(kind, msg):
        fails.setdefault(kind, []).append(msg)

    try:
        root = ET.parse(path).getroot()
        W, H = map(float, root.get("viewBox").split()[2:])
    except (ET.ParseError, AttributeError, ValueError) as e:
        return {"xml": [str(e)]}, {}
    canvas = (0, 0, W, H)
    parent = {c: p for p in root.iter() for c in p}

    ids = [el.get("id") for el in root.iter() if el.get("id")]
    for dup in sorted({i for i in ids if ids.count(i) > 1}):
        fail("ids", f"id {dup!r} is used {ids.count(dup)} times")

    # the canvas colour tells the theme; icons may only use that theme's palette colours
    bg = next((c.get("fill", "").lower() for c in root if tag(c) == "rect"), "")
    theme = next((th for th in THEMES.values() if th["bg"] == bg), None)
    allowed = None if theme is None else {
        v.lower() for pal in theme["palettes"].values() for v in pal.values()} | {theme["paper"].lower(), "none"}

    nodes, labels, pills, edges = {}, [], [], []
    for el in root.iter():
        role = el.get("data-graph-role")
        if role == "node":
            cx, cy = map(float, re.findall(NUM, el.get("transform"))[:2])
            r = float(el.find(f"{NS}circle").get("r"))
            nid = el.get("id")[len("node-"):]
            nodes[nid] = (cx, cy, r)
            icon = f"node {nid!r} ({el.get('data-icon')} icon)"
            # the medallion's turning ring is one animation; the icon must bring its own
            if sum(tag(a) in ("animate", "animateTransform", "animateMotion") for a in el.iter()) < 2:
                fail("icon", f"{icon} has no micro-interaction")
            if allowed is not None:
                used = {c.lower() for a in el.iter() for k in ("fill", "stroke", "values")
                        for c in re.findall(r"#[0-9a-fA-F]{3,6}\b", a.get(k, ""))}
                if used - allowed:
                    fail("icon", f"{icon} uses colours outside the palette: {', '.join(sorted(used - allowed))}")
        elif role == "label":
            s, fs = "".join(el.itertext()), float(el.get("font-size", 12))
            x, y, w = float(el.get("x")), float(el.get("y")), text_width(s, fs)
            labels.append((f"label {s!r}", (x - w / 2, y - 0.8 * fs, x + w / 2, y + 0.25 * fs)))
        elif role == "edge-label":
            rc = el.find(f"{NS}rect")
            x, y, w, h = (float(rc.get(k)) for k in ("x", "y", "width", "height"))
            pills.append((f"edge label {''.join(el.itertext())!r}", (x, y, x + w, y + h)))
        elif role == "edge":
            edges.append((el.get("id"), el.get("data-edge-source"), el.get("data-edge-target"), sample(el.get("d"))))

    node_boxes = [(f"node {k!r}", (x - r, y - r, x + r, y + r)) for k, (x, y, r) in nodes.items()]

    for name, box in node_boxes + labels + pills:
        if box[0] < 0 or box[1] < 0 or box[2] > W or box[3] > H:
            fail("canvas", f"{name} exceeds the {W:g}x{H:g} viewBox")
    for eid, _, _, pts in edges:
        if any(not (0 <= x <= W and 0 <= y <= H) for x, y in pts):
            fail("canvas", f"{eid} exceeds the viewBox")

    for eid, src, tgt, pts in edges:
        for k, (x, y, r) in nodes.items():
            if k not in (src, tgt) and any(math.hypot(px - x, py - y) < r for px, py in pts):
                fail("edge_node", f"{eid} passes through node {k!r}")

    things = node_boxes + labels + pills
    for i, (a, ba) in enumerate(things):
        for b, bb in things[i + 1:]:
            if boxes_overlap(ba, bb) and not (a.startswith("node") and b.startswith("node")):
                fail("label", f"{a} overlaps {b}")

    for name, box in pills:
        # the pill sits on its own edge's midpoint, so the nearest edge owns it
        centre = ((box[0] + box[2]) / 2, (box[1] + box[3]) / 2)
        _, src, tgt, _ = min(edges, key=lambda e: min(math.dist(centre, p) for p in e[3]))
        for eid, a, b, pts in edges:
            if {a, b} != {src, tgt} and any(seg_hits_box(p, q, box) for p, q in zip(pts, pts[1:])):
                warns.setdefault("label_edge", []).append(f"{eid} runs under {name}")

    for i, (ea, _, _, pa) in enumerate(edges):
        for eb, _, _, pb in edges[i + 1:]:
            for p, q in zip(pa, pa[1:]):
                hit = next((x for r_, s in zip(pb, pb[1:]) if (x := seg_cross(p, q, r_, s))), None)
                if hit:
                    warns.setdefault("crossing", []).append(f"{ea} crosses {eb} at {hit[0]:.0f},{hit[1]:.0f}")
                    break

    def fades_out(el):
        # draw mode: connector groups fade to 0 before the loop restarts, which hides any seam inside
        while el is not None:
            if tag(el) == "g" and any(tag(c) == "animate" and c.get("attributeName") == "opacity"
                                      and c.get("values", "").endswith(";0") for c in el):
                return True
            el = parent.get(el)
        return False

    def owner(el):
        # nearest ancestor with an id, so a bad animation can be traced to its node and icon
        while el is not None and not el.get("id"):
            el = parent.get(el)
        if el is None:
            return "the svg"
        return el.get("id") + (f" ({el.get('data-icon')} icon)" if el.get("data-icon") else "")

    for el in root.iter():
        if tag(el) in ("animate", "animateTransform", "animateMotion") and el.get("repeatCount") == "indefinite":
            dur, begin = seconds(el.get("dur")), seconds(el.get("begin"))
            where = f"{tag(el)} {el.get('attributeName') or 'motion'} in {owner(el)}"
            if begin > 0:
                fail("loop", f"{where}: begin={begin:g}s is positive, so it sits still at the start; use a negative begin")
            ratio = loop / dur if dur else 0
            if abs(ratio - round(ratio)) > 1e-3 and not fades_out(el):
                fail("loop", f"{where}: dur={dur:g}s does not divide the {loop:g}s loop, so the GIF jumps at the seam")
    return fails, warns


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="check an animated diagram SVG")
    ap.add_argument("svg")
    ap.add_argument("--loop", type=float, default=6.0, help="loop length in seconds (capture.py seconds)")
    args = ap.parse_args()
    fails, warns = check(Path(args.svg), args.loop)
    for kind in ("xml", "ids", "canvas", "edge_node", "label", "loop", "icon"):
        found = fails.get(kind, [])
        print(f"{'FAIL' if found else 'ok  '} {kind}" + (f" ({len(found)})" if found else ""))
        for msg in found[:8]:
            print(f"       {msg}")
        if len(found) > 8:
            print(f"       ... {len(found) - 8} more")
    for kind in ("label_edge", "crossing"):
        for msg in warns.get(kind, []):
            print(f"warn {kind}: {msg}")
    sys.exit(1 if fails else 0)
