from icons._svg import anim, xform

KEY = "key"
SHAPE = "key"
MOTION = "key wiggles on its bow, ring spreads from the bow"


def draw(p, uid="", label=""):
    paper = p["paper"]
    ink, hi, tint = p["ink"], p["hi"], p["tint"]
    return f"""
<g transform="rotate(-35)">
  <g>{xform('rotate', ['0 -12 0', '16 -12 0', '0 -12 0'], [0, .5, 1], dur=3)}
    <rect x="-4" y="-2.2" width="27" height="4.4" rx="2.2" fill="{paper}" stroke="{ink}" stroke-width="2"/>
    <rect x="12" y="2" width="4.2" height="8" rx="1" fill="{paper}" stroke="{ink}" stroke-width="2"/>
    <rect x="19" y="2" width="4.2" height="6" rx="1" fill="{paper}" stroke="{ink}" stroke-width="2"/>
    <circle cx="-12" cy="0" r="10" fill="{paper}" stroke="{ink}" stroke-width="2"/>
    <circle cx="-12" cy="0" r="3.4" fill="{tint}" stroke="{ink}" stroke-width="1.6"/>
    <circle cx="-12" cy="0" r="10" fill="none" stroke="{hi}" stroke-width="1.6" opacity="0">
      {anim('r', [10, 17], [0, 1], dur=1.5)}{anim('opacity', [.8, 0], [0, 1], dur=1.5)}</circle>
  </g>
</g>"""
