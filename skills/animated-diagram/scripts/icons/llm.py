from icons._svg import xform

KEY = "llm"
SHAPE = "sparkle star in a rounded tile"
MOTION = "star pulses, small sparkles twinkle"


def draw(p, uid="", label=""):
    paper = p["paper"]
    ink, hi = p["ink"], p["hi"]
    star = "M0,-1 Q.1,-.1 1,0 Q.1,.1 0,1 Q-.1,.1 -1,0 Q-.1,-.1 0,-1z"
    return f"""
<rect x="-21" y="-21" width="42" height="42" rx="11" fill="{paper}" stroke="{ink}" stroke-width="2"/>
<g>{xform('scale', ['11', '15', '11'], [0, .5, 1], dur=1.5)}<path d="{star}" fill="{hi}" stroke="{ink}" stroke-width=".12" stroke-linejoin="round"/></g>
<g transform="translate(12,-12)"><g>{xform('scale', ['.3', '4.5', '.3'], [0, .5, 1], dur=1.2)}<path d="{star}" fill="{ink}"/></g></g>
<g transform="translate(-12,12)"><g>{xform('scale', ['4.5', '.3', '4.5'], [0, .5, 1], dur=1.2)}<path d="{star}" fill="{ink}"/></g></g>"""
