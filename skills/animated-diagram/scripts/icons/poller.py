import math

from icons._svg import anim, n, xform

KEY = "poller"
SHAPE = "document + circular arrows"
MOTION = "arrow ring rotates, last line blinks"


def arc_pts(r, a):
    return r * math.cos(math.radians(a)), r * math.sin(math.radians(a))


def arc_arrow(r, a0, a1, color):
    x0, y0 = arc_pts(r, a0)
    x1, y1 = arc_pts(r, a1)
    d = f"M{n(x0)},{n(y0)} A{r},{r} 0 0 1 {n(x1)},{n(y1)}"
    tx, ty = -math.sin(math.radians(a1)), math.cos(math.radians(a1))
    nx, ny = -ty, tx
    tip = (x1 + tx * 5.5, y1 + ty * 5.5)
    b1 = (x1 + nx * 4.2, y1 + ny * 4.2)
    b2 = (x1 - nx * 4.2, y1 - ny * 4.2)
    return (f'<path d="{d}" fill="none" stroke="{color}" stroke-width="2.2" stroke-linecap="round"/>'
            f'<polygon points="{n(tip[0])},{n(tip[1])} {n(b1[0])},{n(b1[1])} {n(b2[0])},{n(b2[1])}" fill="{color}"/>')


def draw(p, uid="", label=""):
    paper = p["paper"]
    ink, hi = p["ink"], p["hi"]
    return f"""
<g>{xform('rotate', ['0','360'], dur=3)}{arc_arrow(21, 195, 305, hi)}{arc_arrow(21, 15, 125, hi)}</g>
<path d="M-8,-10 h10 l6,6 v14 h-16 z" fill="{paper}" stroke="{ink}" stroke-width="2" stroke-linejoin="round"/>
<path d="M2,-10 v6 h6" fill="none" stroke="{ink}" stroke-width="1.6" stroke-linejoin="round"/>
<line x1="-4" y1="1" x2="4" y2="1" stroke="{ink}" stroke-width="1.6" stroke-linecap="round"/>
<line x1="-4" y1="5" x2="2" y2="5" stroke="{hi}" stroke-width="1.6" stroke-linecap="round">{anim('opacity', [1, .15, 1], [0, .5, 1], dur=1.5)}</line>"""
