from icons._svg import anim, xform

KEY = "browser"
SHAPE = "browser window + React-style atom"
MOTION = "atom spins, nucleus pulses"


def draw(p, uid="", label=""):
    paper = p["paper"]
    ink, hi = p["ink"], p["hi"]
    ellipses = "".join(
        f'<ellipse rx="12" ry="4.6" transform="rotate({a})" fill="none" stroke="{hi}" stroke-width="1.8"/>'
        for a in (0, 60, 120)
    )
    return f"""
<rect x="-24" y="-20" width="48" height="40" rx="5" fill="{paper}" stroke="{ink}" stroke-width="2"/>
<line x1="-24" y1="-11" x2="24" y2="-11" stroke="{ink}" stroke-width="2"/>
<circle cx="-18" cy="-15.5" r="1.4" fill="{ink}"/><circle cx="-13" cy="-15.5" r="1.4" fill="{ink}"/><circle cx="-8" cy="-15.5" r="1.4" fill="{ink}"/>
<g transform="translate(0,5)">
  <g>{xform('rotate', ['0','360'], dur=6)}{ellipses}</g>
  <circle r="2.4" fill="{hi}">{anim('r', [2.4, 3.4, 2.4], [0, .5, 1], dur=1.5)}</circle>
</g>"""
