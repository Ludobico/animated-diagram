from icons._svg import anim, cylinder

KEY = "database"
SHAPE = "cylinder + rows"
MOTION = "rows highlight in turn, top dot pulses"


def draw(p, uid="", label=""):
    ink, hi = p["ink"], p["hi"]
    rows = ""
    for i, y in enumerate((-4, 4.5, 13)):
        rows += (f'<line x1="-10" y1="{y}" x2="10" y2="{y}" stroke="{ink}" stroke-width="2" stroke-linecap="round" opacity=".45"/>'
                 f'<line x1="-10" y1="{y}" x2="10" y2="{y}" stroke="{hi}" stroke-width="2.6" stroke-linecap="round" opacity="0">'
                 f'{anim("opacity", [0, 1, 1, 0, 0], [0, .1, .3, .4, 1], dur=1.5, begin=-1.5 + 0.35 * i)}</line>')
    return f"""
{cylinder(p, uid)}
<path d="M-19,2 A19,6 0 0 0 19,2" fill="none" stroke="{ink}" stroke-width="1.6" opacity=".7"/>
<path d="M-19,9 A19,6 0 0 0 19,9" fill="none" stroke="{ink}" stroke-width="1.6" opacity=".7"/>
<g clip-path="url(#cl-{uid})">{rows}</g>
<ellipse cx="0" cy="-14" rx="19" ry="6" fill="{p['tint']}" stroke="{ink}" stroke-width="2"/>
<g transform="translate(0,-14)"><circle r="1.9" fill="{hi}">{anim('r', [1.9, 3, 1.9], [0, .5, 1], dur=1.5)}</circle></g>"""
