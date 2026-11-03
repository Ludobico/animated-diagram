from icons._svg import anim, xform

KEY = "cloud"
SHAPE = "cloud + up arrow"
MOTION = "arrow rises and fades"


def draw(p, uid="", label=""):
    paper = p["paper"]
    ink, hi = p["ink"], p["hi"]
    return f"""
<path d="M-14,12 H12 A10,10 0 0 0 13,-8 A14,14 0 0 0 -13,-4 A9,9 0 0 0 -14,12 Z" fill="{paper}" stroke="{ink}" stroke-width="2" stroke-linejoin="round"/>
<g>{xform('translate', ['0 7', '0 -5', '0 -5'], [0, .7, 1], dur=1.5)}{anim('opacity', [0, 1, 0], [0, .4, 1], dur=1.5)}
  <line x1="0" y1="-2" x2="0" y2="9" stroke="{hi}" stroke-width="2.4" stroke-linecap="round"/>
  <polyline points="-4.5,2 0,-3 4.5,2" fill="none" stroke="{hi}" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"/></g>"""
