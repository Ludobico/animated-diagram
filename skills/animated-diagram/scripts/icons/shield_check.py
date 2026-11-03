from icons._svg import anim, xform

KEY = "shield-check"
SHAPE = "shield + check mark"
MOTION = "check mark draws and erases, outline spreads"


def draw(p, uid="", label=""):
    paper = p["paper"]
    ink, hi = p["ink"], p["hi"]
    d = "M0,-23 L18,-15 V2 Q18,17 0,25 Q-18,17 -18,2 V-15 Z"
    return f"""
<path d="{d}" fill="{paper}" stroke="{ink}" stroke-width="2" stroke-linejoin="round"/>
<path d="{d}" fill="none" stroke="{hi}" stroke-width="1.6" stroke-linejoin="round" opacity="0">
  {xform('scale', ['1', '1.3'], dur=3)}{anim('opacity', [.8, 0], [0, 1], dur=3)}</path>
<path d="M-8,2 L-2,9 L9,-6" fill="none" stroke="{hi}" stroke-width="3.4" stroke-linecap="round" stroke-linejoin="round"
  pathLength="100" stroke-dasharray="100" stroke-dashoffset="100">
  {anim('stroke-dashoffset', [100, 0, 0, 100], [0, .35, .8, 1], dur=3)}</path>"""
