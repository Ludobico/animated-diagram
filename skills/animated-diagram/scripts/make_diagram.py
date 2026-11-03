#!/usr/bin/env python3
"""Spec-driven animated architecture SVG (SMIL) generator.

    python make_diagram.py spec.json out.svg [--lines draw|static] [--theme light|dark] [--extra-icons my_icon.py ...]

The spec is a small JSON topology (see ../examples/*.json and SKILL.md). Layout is
automatic: one column per group (left -> right), nodes spread evenly down each column,
edges as horizontal Beziers with separate ports, vertical lines inside a column.
Every node gets a hand-drawn icon (explicit `icon`, otherwise guessed from its label).

Timeline (T = 6 s):
  draw   connectors draw on, packets flow, connectors fade out, loop.
  static connectors, arrowheads and edge labels are visible from the first frame; only packets move.
All icon micro-animations use periods that divide T so the GIF loops seamlessly.
"""
import argparse
import json
import math
import re
from pathlib import Path

from icons import ICONS, T, anim, guess_icon, load_extra, n

FONT = "'Pretendard','Segoe UI','Malgun Gothic','Noto Sans KR','Apple SD Gothic Neo',sans-serif"
FADE_START = 5.5

# Per theme: canvas `bg`, `paper` (node rims, icon and label fills), `text` / `muted` (node labels),
# and one palette per group colour: ink (icon outline), hi (icon accent), tint (node face),
# line (edge), acc (arrowhead, packets, edge-label text, group title).
# Dark uses GitHub's dark background so it blends into a README; every pair is at least as
# readable as in light (contrast ratios checked when the palette was made).
THEMES = {
    "light": dict(bg="#ffffff", paper="#fff", text="#1f2937", muted="#64748b", palettes={
        "purple": dict(ink="#5b3a9a", hi="#8b5cf6", tint="#f4efff", line="#cdbfee", acc="#7b4cc2"),
        "blue": dict(ink="#23378f", hi="#3b6fe0", tint="#edf1ff", line="#bcc7ee", acc="#2a3fa0"),
        "green": dict(ink="#0a7a55", hi="#10b981", tint="#e6f6ef", line="#b4e3cf", acc="#0b8f63"),
        "orange": dict(ink="#9a4a06", hi="#f59e0b", tint="#fff4e5", line="#f3d3a3", acc="#d97706"),
        "teal": dict(ink="#0f5f5a", hi="#14b8a6", tint="#e6f7f5", line="#b2e4de", acc="#0d9488"),
        "rose": dict(ink="#9f1239", hi="#f43f5e", tint="#ffecef", line="#f6c1cb", acc="#be123c"),
        "slate": dict(ink="#334155", hi="#64748b", tint="#f1f5f9", line="#cbd5e1", acc="#475569"),
    }),
    "dark": dict(bg="#0d1117", paper="#161b22", text="#e6edf3", muted="#8b949e", palettes={
        "purple": dict(ink="#c4b5fd", hi="#a78bfa", tint="#211a35", line="#4c3d78", acc="#b197fc"),
        "blue": dict(ink="#a5c8ff", hi="#60a5fa", tint="#14233b", line="#2f4a78", acc="#79b0ff"),
        "green": dict(ink="#86efc4", hi="#34d399", tint="#0f2a22", line="#1f5a47", acc="#4cd8a5"),
        "orange": dict(ink="#fcd38d", hi="#fbbf24", tint="#2d2110", line="#6b4c1c", acc="#f5b544"),
        "teal": dict(ink="#7de8da", hi="#2dd4bf", tint="#0e2a28", line="#1d5652", acc="#3fd2c0"),
        "rose": dict(ink="#fdb0bb", hi="#fb7185", tint="#33151d", line="#6e2e3d", acc="#fb8a9b"),
        "slate": dict(ink="#cbd5e1", hi="#94a3b8", tint="#1c2330", line="#3d4a5c", acc="#a3b1c4"),
    }),
}
AUTO_COLORS = ["purple", "blue", "green", "orange", "teal", "rose", "slate"]


def palette(theme, color):
    """Group palette with the theme's paper colour, as icons receive it."""
    th = THEMES[theme]
    if color not in th["palettes"]:
        raise SystemExit(f"unknown color {color!r}; choose from {sorted(th['palettes'])}")
    return dict(th["palettes"][color], paper=th["paper"])

SIZES = {"sm": (34, 1.0), "md": (40, 1.12), "lg": (48, 1.35)}
MARGIN, COL_W, GAP = 24, 250, 220
LABEL_DROP = 62  # medallion edge -> bottom of the two-line label
LABEL_CLEAR = 14  # gap between a sender-side edge label and the start of its edge


def esc(s):
    return str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def text_width(s, size):
    return sum(size * (1.0 if ord(c) > 127 else 0.58) for c in s)


def bezier(p0, p1, p2, p3, t):
    u = 1 - t
    return tuple(u ** 3 * a + 3 * t * u * u * b + 3 * t * t * u * c + t ** 3 * d for a, b, c, d in zip(p0, p1, p2, p3))


def label_t(ctrl, width):
    """Where on its edge a label of a two-way pair goes: as close to the sender as the pill allows.

    Both labels of A->B / B->A would otherwise stack at the midpoint, because the two edges run only
    a port gap apart. Walking t up from the source until the pill clears the start of the edge puts
    each label next to the node that sends that data; past the midpoint there is no room, so stop there.
    """
    x0, y0 = ctrl[0]
    for i in range(5, 51):
        x, y = bezier(*ctrl, i / 100)
        if abs(x - x0) >= width / 2 + LABEL_CLEAR or abs(y - y0) >= 14 + LABEL_CLEAR:
            return i / 100
    return 0.5


def medallion(r, sc, p, icon_svg):
    """Node disc: white rim, tinted face, a slowly turning dashed ring, and the icon scaled on top."""
    return (f'<circle r="{r}" fill="{p["paper"]}"/><circle r="{r - 4}" fill="{p["tint"]}"/>'
            f'<circle r="{r - 1}" fill="none" stroke="{p["acc"]}" stroke-width="1.7" stroke-dasharray="1.5 6" stroke-linecap="round">'
            f'{anim("stroke-dashoffset", [0, -7.5], [0, 1], dur=1.5)}</circle>'
            f'<g transform="scale({sc})">{icon_svg}</g>')


def load_spec(path):
    spec = json.loads(Path(path).read_text(encoding="utf-8"))
    groups = spec.get("groups") or []
    nodes = spec.get("nodes") or []
    edges = spec.get("edges") or []
    if not groups or not nodes:
        raise SystemExit("spec needs at least one group and one node")
    gids = [g["id"] for g in groups]
    nids = [x["id"] for x in nodes]
    if len(set(gids)) != len(gids) or len(set(nids)) != len(nids):
        raise SystemExit("duplicate group or node ids")
    for x in nodes:
        if x.get("group") not in gids:
            raise SystemExit(f"node {x['id']!r}: unknown group {x.get('group')!r}")
    for e in edges:
        for k in ("from", "to"):
            if e[k] not in nids:
                raise SystemExit(f"edge {e}: unknown node {e[k]!r}")
        if e["from"] == e["to"]:
            raise SystemExit(f"edge {e}: self loops are not supported")
    return spec


def optimize_order(cols, edges):
    """Barycenter sweeps to cut crossings (only when spec.optimize_order is true)."""
    pos = {nid: i / max(len(c) - 1, 1) for c in cols for i, nid in enumerate(c)}
    nbrs = {}
    for e in edges:
        nbrs.setdefault(e["from"], []).append(e["to"])
        nbrs.setdefault(e["to"], []).append(e["from"])
    for sweep in (range(1, len(cols)), range(len(cols) - 2, -1, -1)):
        for ci in sweep:
            # snapshot the column: during list.sort() CPython shows the list as empty to the key function
            same = set(cols[ci])

            def key(nid):
                ns = [pos[m] for m in nbrs.get(nid, []) if m not in same]
                return sum(ns) / len(ns) if ns else pos[nid]
            cols[ci].sort(key=key)
            for i, nid in enumerate(cols[ci]):
                pos[nid] = i / max(len(cols[ci]) - 1, 1)
    # inside one column a producer should sit above the node it feeds
    for c in cols:
        for _ in range(len(c)):
            moved = False
            for e in edges:
                a, b = e["from"], e["to"]
                if a in c and b in c and c.index(a) > c.index(b):
                    c.remove(a)
                    c.insert(c.index(b), a)
                    moved = True
            if not moved:
                break
    return cols


def build(spec, lines="draw", port_gap=10.0, theme="light"):
    groups, nodes_in, edges_in = spec["groups"], spec["nodes"], spec["edges"]
    static = lines == "static"
    th = THEMES[theme]
    paper = th["paper"]
    title = spec.get("title")
    top = 64 if title else 28

    colors = {g["id"]: palette(theme, g.get("color") or AUTO_COLORS[i % len(AUTO_COLORS)]) for i, g in enumerate(groups)}

    icon_of = {x["id"]: x.get("icon") or guess_icon(x["label"], x.get("sub", ""), x.get("shape")) for x in nodes_in}
    missing = [x for x in nodes_in if icon_of[x["id"]] is None]
    if missing:
        raise SystemExit("no icon for: " + ", ".join(f'{x["id"]} ({x["label"]!r})' for x in missing) +
                         '\nset "icon" on these nodes: a key from references/icons.md, '
                         "or draw one (references/custom-icons.md)")
    unknown = [f"{nid} ({key!r})" for nid, key in icon_of.items() if key not in ICONS]
    if unknown:
        raise SystemExit(f"unknown icon for: {', '.join(unknown)}; choose from {sorted(ICONS)} "
                         "or pass the drawn icon with --extra-icons")

    byid = {x["id"]: x for x in nodes_in}
    deg = {nid: 0 for nid in byid}
    for e in edges_in:
        deg[e["from"]] += 1
        deg[e["to"]] += 1

    cols = [[x["id"] for x in nodes_in if x["group"] == g["id"]] for g in groups]
    if spec.get("optimize_order"):
        cols = optimize_order(cols, edges_in)
    col_of = {nid: ci for ci, c in enumerate(cols) for nid in c}
    idx_of = {nid: i for c in cols for i, nid in enumerate(c)}

    # ---- geometry
    ncols = len(groups)
    W = 2 * MARGIN + ncols * COL_W + (ncols - 1) * GAP
    # vertical gaps: 120 normally, 200 where a vertical edge joins neighbours (room for the line + arrow)
    pairs = {frozenset((e["from"], e["to"])) for e in edges_in}
    gaps = [[200 if frozenset((c[j], c[j + 1])) in pairs else 120 for j in range(len(c) - 1)] for c in cols]
    span = max([240] + [sum(g) for g in gaps])
    y0 = top + 100
    gh = span + 210
    H = top + gh + 24

    geo = {}
    for ci, c in enumerate(cols):
        cx = MARGIN + ci * (COL_W + GAP) + COL_W / 2
        scale = span / sum(gaps[ci]) if len(c) > 1 else 1
        for i, nid in enumerate(c):
            cy = y0 + span / 2 if len(c) == 1 else y0 + sum(gaps[ci][:i]) * scale
            nd = byid[nid]
            size = nd.get("size") or ("lg" if deg[nid] >= 4 else "md" if deg[nid] == 3 else "sm")
            r, sc = SIZES[size]
            geo[nid] = dict(cx=cx, cy=cy, r=r, sc=sc)

    # ---- ports: spread edges that share one side of a node
    sides = {}
    for k, e in enumerate(edges_in):
        a, b = e["from"], e["to"]
        ca, cb = col_of[a], col_of[b]
        if ca == cb:
            e["_kind"] = "vertical" if abs(idx_of[a] - idx_of[b]) == 1 else "bulge"
        else:
            e["_kind"] = "h"
        if e["_kind"] == "h":
            s = 1 if cb > ca else -1
            sides.setdefault((a, s), []).append((k, "src", geo[b]["cy"]))
            sides.setdefault((b, -s), []).append((k, "tgt", geo[a]["cy"]))
        elif e["_kind"] == "bulge":
            sides.setdefault((a, 1), []).append((k, "src", geo[b]["cy"]))
            sides.setdefault((b, 1), []).append((k, "tgt", geo[a]["cy"]))
    dy = {}
    for (nid, _s), lst in sides.items():
        lst.sort(key=lambda t: t[2])
        # wider gaps separate the labels of an A->B / B->A pair, but crowd nodes with many edges on one side
        step = min(port_gap, geo[nid]["r"] * 0.65 / max((len(lst) - 1) / 2, 1))
        for i, (k, role, _y) in enumerate(lst):
            dy[(k, role)] = (i - (len(lst) - 1) / 2) * step

    # ---- svg
    out = []
    desc = "; ".join(f"{byid[e['from']]['label']} to {byid[e['to']]['label']}" for e in edges_in)
    out.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {n(W)} {n(H)}" width="{n(W)}" height="{n(H)}" role="img" '
               f'aria-labelledby="t d" font-family="{FONT}" data-style="1" data-diagram-type="architecture" '
               f'data-semantic-profile="custom-animated-architecture">')
    out.append(f'<title id="t">{esc(title or "Architecture overview")}</title><desc id="d">{esc(desc)}</desc>')
    out.append(f'<rect width="{n(W)}" height="{n(H)}" fill="{th["bg"]}"/>')
    if title:
        out.append(f'<text x="{MARGIN}" y="38" font-size="24" font-weight="700" fill="{th["text"]}">{esc(title)}</text>')

    for ci, g in enumerate(groups):
        p = colors[g["id"]]
        x = MARGIN + ci * (COL_W + GAP)
        out.append(f'<g data-graph-role="container" data-group="{esc(g["id"])}">'
                   f'<rect x="{n(x)}" y="{n(top)}" width="{COL_W}" height="{n(gh)}" rx="22" fill="none" stroke="{p["acc"]}" '
                   f'stroke-width="1.6" stroke-dasharray="2 6" stroke-linecap="round" opacity=".7"/>'
                   f'<text x="{n(x + COL_W / 2)}" y="{n(top + 38)}" text-anchor="middle" font-size="21" font-weight="700" '
                   f'fill="{p["acc"]}" letter-spacing=".3">{esc(g["title"])}</text></g>')

    fade = "" if static else anim("opacity", [1, 1, 0], [0, FADE_START / T, 1])
    ne = len(edges_in)
    step = min(0.1, 1.2 / max(ne - 1, 1))
    below, above, labels = [], [], []
    labelled = {(e["from"], e["to"]) for e in edges_in if e.get("label")}

    for k, e in enumerate(edges_in):
        a, b = e["from"], e["to"]
        ga, gb = geo[a], geo[b]
        acc, line = colors[byid[a]["group"]]["acc"], colors[byid[a]["group"]]["line"]
        kind = e["_kind"]
        sdy, tdy = dy.get((k, "src"), 0), dy.get((k, "tgt"), 0)
        if kind == "vertical":
            down = geo[b]["cy"] > ga["cy"]
            if down:
                x1, y1 = ga["cx"], ga["cy"] + ga["r"] + LABEL_DROP
                ax, ay, rot = gb["cx"], gb["cy"] - gb["r"], 90
                d = f"M{n(x1)},{n(y1 + 4.9)} L{n(ax)},{n(ay - 9.6)}"
            else:
                x1, y1 = ga["cx"], ga["cy"] - ga["r"]
                ax, ay, rot = gb["cx"], gb["cy"] + gb["r"] + LABEL_DROP, -90
                d = f"M{n(x1)},{n(y1 - 4.9)} L{n(ax)},{n(ay + 9.6)}"
            ctrl = ((x1, y1), (x1, y1), (ax, ay), (ax, ay))
            length = abs(ay - y1)
        elif kind == "bulge":
            x1, y1 = ga["cx"] + math.sqrt(max(ga["r"] ** 2 - sdy ** 2, 0)), ga["cy"] + sdy
            ax, ay = gb["cx"] + math.sqrt(max(gb["r"] ** 2 - tdy ** 2, 0)), gb["cy"] + tdy
            rot = 180
            xs, xe = x1 + 4.9, ax + 9.6
            bx = max(xs, xe) + 110
            d = f"M{n(xs)},{n(y1)} C{n(bx)},{n(y1)} {n(bx)},{n(ay)} {n(xe)},{n(ay)}"
            ctrl = ((xs, y1), (bx, y1), (bx, ay), (xe, ay))
            length = abs(ay - y1) + 200
        else:
            s = 1 if col_of[b] > col_of[a] else -1
            x1, y1 = ga["cx"] + s * math.sqrt(max(ga["r"] ** 2 - sdy ** 2, 0)), ga["cy"] + sdy
            ax, ay = gb["cx"] - s * math.sqrt(max(gb["r"] ** 2 - tdy ** 2, 0)), gb["cy"] + tdy
            rot = 0 if s > 0 else 180
            xs, xe = x1 + s * 4.9, ax - s * 9.6
            c1, c2 = xs + (xe - xs) * 0.55, xe - (xe - xs) * 0.55
            d = f"M{n(xs)},{n(y1)} C{n(c1)},{n(y1)} {n(c2)},{n(ay)} {n(xe)},{n(ay)}"
            ctrl = ((xs, y1), (c1, y1), (c2, ay), (xe, ay))
            length = abs(xe - xs) + abs(ay - y1) * 0.3
        ds = 0.2 + k * step
        de = ds + 0.6
        a0, a1 = ds / T, de / T
        dur = max(1.6, min(3.0, length / 180))
        if static:
            # nothing resets at the loop end, so a packet period that does not divide T would jump at the seam
            dur = min((T / 4, T / 3, T / 2, T), key=lambda c: abs(c - dur))
        eid = f"edge-{a}-{b}-{k}"
        path = (f'<path id="{esc(eid)}" data-graph-role="edge" data-edge-source="{esc(a)}" data-edge-target="{esc(b)}" d="{d}" '
                f'fill="none" stroke="{line}" stroke-width="2.4" pathLength="100"')
        head = f'<polygon points="0,0 -9,-5 -9,5" fill="{acc}" transform="translate({n(ax)},{n(ay)}) rotate({rot})"'
        if static:
            below.append(path + "/>")
            above.append(head + "/>")
        else:
            # draw: the connector is drawn on, then its arrowhead, packets and label appear
            below.append(f'{path} stroke-dasharray="100" stroke-dashoffset="100">'
                         f'{anim("stroke-dashoffset", [100, 100, 0, 0], [0, a0, a1, 1])}</path>')
            above.append(f'{head} opacity="0">{anim("opacity", [0, 0, 1, 1], [0, max(a1 - 0.02, 0), a1, 1])}</polygon>')
        above.append(f'<circle cx="{n(x1)}" cy="{n(y1)}" r="4" fill="{acc}" stroke="{paper}" stroke-width="1.5"/>')
        pk = ["<g>" if static else f'<g opacity="0">{anim("opacity", [0, 0, 1, 1], [0, a1, a1 + 0.02, 1])}']
        phase = (k * 0.37) % dur
        for j in range(2):
            off = phase + j * dur / 2
            for lag, r, op in ((0.0, 4.6, 1), (0.07, 3.2, .5), (0.14, 2.2, .3)):
                stroke = f' stroke="{paper}" stroke-width="1.6"' if lag == 0 else ""
                # keep begin <= 0: a tail dot with a positive begin waits at the SVG origin (0,0) until it starts
                pk.append(f'<circle r="{r}" fill="{acc}" opacity="{op}"{stroke}>'
                          f'<animateMotion dur="{n(dur)}s" begin="{n(-((off - lag) % dur))}s" repeatCount="indefinite" path="{d}" calcMode="linear"/></circle>')
            pk.append(f'<circle cx="{n(ax)}" cy="{n(ay)}" r="3" fill="none" stroke="{acc}" stroke-width="2" opacity="0">'
                      f'{anim("opacity", [0, 0, .75, 0], [0, .88, .9, 1], dur=dur, begin=-off)}'
                      f'{anim("r", [3, 3, 3, 14], [0, .88, .9, 1], dur=dur, begin=-off)}</circle>')
        pk.append("</g>")
        above.append("".join(pk))
        if e.get("label"):
            tw = text_width(e["label"], 13) + 28
            # one-way edges keep the label at the midpoint; a labelled two-way pair moves each label to its sender
            mid = bezier(*ctrl, label_t(ctrl, tw) if (b, a) in labelled else 0.5)
            lx, ly = mid[0] - tw / 2, mid[1]
            start = ('<g data-graph-role="edge-label">' if static else
                     f'<g opacity="0" data-graph-role="edge-label">{anim("opacity", [0, 0, 1, 1], [0, a1 - .02, a1, 1])}')
            labels.append(
                start +
                f'<rect x="{n(lx)}" y="{n(ly - 14)}" width="{n(tw)}" height="28" rx="14" fill="{paper}" stroke="{line}" stroke-width="1.6"/>'
                f'<text x="{n(lx + tw / 2)}" y="{n(ly + 4.5)}" text-anchor="middle" font-size="13" font-weight="600" fill="{acc}">{esc(e["label"])}</text></g>')

    out.append(f'<g id="connectors-under">{fade}{"".join(below)}</g>')

    for nid, nd in byid.items():
        g_ = geo[nid]
        p = colors[nd["group"]]
        key = icon_of[nid]
        uid ="".join(ch if ch.isalnum() else "_" for ch in nid)
        r, sc = g_["r"], g_["sc"]
        out.append(
            f'<g id="node-{esc(nid)}" data-graph-role="node" data-group="{esc(nd["group"])}" data-icon="{key}" '
            f'transform="translate({n(g_["cx"])},{n(g_["cy"])})">'
            f'{medallion(r, sc, p, ICONS[key](p, uid, nd["label"]))}</g>')
        ly = g_["cy"] + r + 24
        label = nd["label"]
        fs = 16 if r >= 48 else (13.5 if len(label) > 20 else 15)
        out.append(f'<text x="{n(g_["cx"])}" y="{n(ly)}" text-anchor="middle" font-size="{fs}" font-weight="700" fill="{th["text"]}" data-graph-role="label">{esc(label)}</text>')
        if nd.get("sub"):
            out.append(f'<text x="{n(g_["cx"])}" y="{n(ly + 19)}" text-anchor="middle" font-size="12.5" fill="{th["muted"]}" data-graph-role="label">{esc(nd["sub"])}</text>')

    out.append(f'<g id="connectors-over">{fade}{"".join(above)}{"".join(labels)}</g>')
    out.append("</svg>")
    return "\n".join(out)


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="spec.json -> animated architecture SVG")
    ap.add_argument("spec")
    ap.add_argument("out")
    ap.add_argument("--lines", choices=["draw", "static"], default="draw",
                    help="draw: connectors draw on and fade each loop; static: connectors always visible")
    ap.add_argument("--theme", choices=sorted(THEMES), default="light",
                    help="light: white canvas; dark: GitHub dark canvas (#0d1117)")
    ap.add_argument("--port-gap", type=float, default=10.0,
                    help="max px between edges that share one side of a node")
    ap.add_argument("--extra-icons", nargs="+", default=[], metavar="FILE",
                    help="icon modules drawn for this job (same format as scripts/icons/*.py)")
    args = ap.parse_args()
    for f in args.extra_icons:
        load_extra(f)
    dest = Path(args.out)
    svg = build(load_spec(args.spec), args.lines, args.port_gap, args.theme)
    dest.write_text(svg, encoding="utf-8")
    print(f"wrote {dest} ({dest.stat().st_size} bytes, lines={args.lines}, theme={args.theme})")
    # the icon each node got, so a wrong keyword guess is easy to spot
    picks = re.findall(r'<g id="node-([^"]*)" data-graph-role="node" data-group="[^"]*" data-icon="([^"]*)"', svg)
    print("icons: " + ", ".join(f"{nid}={key}" for nid, key in picks))
