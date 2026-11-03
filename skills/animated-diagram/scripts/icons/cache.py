from icons._svg import anim, xform

KEY = "cache"
SHAPE = "lightning bolt + slots"
MOTION = "slots blink, bolt pulses"


def draw(p, uid="", label=""):
    paper = p["paper"]
    ink, hi = p["ink"], p["hi"]
    return f"""
<rect x="-22" y="-20" width="44" height="40" rx="8" fill="{paper}" stroke="{ink}" stroke-width="2"/>
<path d="M3,-14 L-8,2 H-1 L-3,14 L9,-3 H2 Z" fill="{hi}" stroke="{ink}" stroke-width="1.6" stroke-linejoin="round">
  {xform('scale', ['1', '1.15', '1'], [0, .5, 1], dur=1.0)}</path>
<line x1="-18" y1="-8" x2="-13" y2="-8" stroke="{hi}" stroke-width="2" stroke-linecap="round">{anim('opacity', [0, 1, 0], [0, .5, 1], dur=1.0)}</line>
<line x1="-18" y1="2" x2="-11" y2="2" stroke="{hi}" stroke-width="2" stroke-linecap="round">{anim('opacity', [1, 0, 1], [0, .5, 1], dur=1.0)}</line>
<line x1="-18" y1="12" x2="-13" y2="12" stroke="{hi}" stroke-width="2" stroke-linecap="round">{anim('opacity', [0, 1, 0], [0, .5, 1], dur=1.0)}</line>"""
