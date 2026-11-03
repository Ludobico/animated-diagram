from icons._svg import xform

KEY = "chip"
SHAPE = "chip + score bars"
MOTION = "bars re-sort by score, then scramble back"


def draw(p, uid="", label=""):
    paper = p["paper"]
    ink, hi = p["ink"], p["hi"]
    pins = ""
    for x in (-9, -3, 3, 9):
        pins += (f'<line x1="{x}" y1="-15" x2="{x}" y2="-21" stroke="{ink}" stroke-width="2" stroke-linecap="round"/>'
                 f'<line x1="{x}" y1="15" x2="{x}" y2="21" stroke="{ink}" stroke-width="2" stroke-linecap="round"/>'
                 f'<line x1="-15" y1="{x}" x2="-21" y2="{x}" stroke="{ink}" stroke-width="2" stroke-linecap="round"/>'
                 f'<line x1="15" y1="{x}" x2="21" y2="{x}" stroke="{ink}" stroke-width="2" stroke-linecap="round"/>')
    unsorted = [9, 19, 6, 13]
    ranked = [19, 13, 9, 6]
    base = 10
    bars = ""
    for i, x in enumerate((-9, -3, 3, 9)):
        hu = unsorted[i]
        # reranker: scores reorder into ranked order, hold, then scramble back
        hs_idx = sorted(range(4), key=lambda k: -unsorted[k]).index(i)
        hs = ranked[hs_idx]
        # slide bar horizontally to ranked slot while height stays
        tx = (-9 + 6 * hs_idx) - x
        bars += (f'<g>{xform("translate", ["0 0", "0 0", f"{tx} 0", f"{tx} 0", "0 0"], [0, .15, .45, .85, 1], dur=3)}'
                 f'<rect x="{x - 2.2}" y="{base - hu}" width="4.4" height="{hu}" rx="1.2" fill="{hi}"/></g>')
    return f"""
{pins}
<rect x="-15" y="-15" width="30" height="30" rx="4.5" fill="{paper}" stroke="{ink}" stroke-width="2"/>
<line x1="-10" y1="{base + 0.5}" x2="10" y2="{base + 0.5}" stroke="{ink}" stroke-width="1.4" opacity=".5"/>
{bars}"""
