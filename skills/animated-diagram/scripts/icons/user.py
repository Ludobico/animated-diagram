from icons._svg import anim

KEY = "user"
SHAPE = "person"
MOTION = "notification dot blinks, ring spreads"


def draw(p, uid="", label=""):
    paper = p["paper"]
    ink, hi = p["ink"], p["hi"]
    return f"""
<circle cx="0" cy="-9" r="9" fill="{paper}" stroke="{ink}" stroke-width="2"/>
<path d="M-18,19 Q-18,4 0,4 Q18,4 18,19 Z" fill="{paper}" stroke="{ink}" stroke-width="2" stroke-linejoin="round"/>
<circle cx="15" cy="-15" r="3.6" fill="{hi}">{anim('opacity', [1, .2, 1], [0, .5, 1], dur=1.5)}</circle>
<circle cx="0" cy="-9" r="9" fill="none" stroke="{hi}" stroke-width="1.6" opacity="0">
  {anim('r', [9, 17], [0, 1], dur=3)}{anim('opacity', [.8, 0], [0, 1], dur=3)}</circle>"""
