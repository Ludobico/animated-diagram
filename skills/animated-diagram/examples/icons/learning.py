from icons._svg import anim, xform

KEY = "learning"
SHAPE = "open book (playbook) + sparkle"
MOTION = "lines are written onto the right page one by one, sparkle pulses"


def draw(p, uid="", label=""):
    ink, hi, paper = p["ink"], p["hi"], p["paper"]
    star = "M0,-6 Q.7,-.7 6,0 Q.7,.7 0,6 Q-.7,.7 -6,0 Q-.7,-.7 0,-6z"
    left = "".join(
        f'<line x1="-18" y1="{y}" x2="-4" y2="{y}" stroke="{ink}" stroke-width="1.6" stroke-linecap="round" opacity=".45"/>'
        for y in (-4, 2, 8))
    right = "".join(
        f'<line x1="4" y1="{y}" x2="4" y2="{y}" stroke="{hi}" stroke-width="2.2" stroke-linecap="round">'
        f'{anim("x2", [4, 4, 18, 18, 4], [0, .1 + .2 * i, .3 + .2 * i, .9, 1], dur=3)}</line>'
        for i, y in enumerate((-4, 2, 8)))
    return f"""
<path d="M-22,-11 Q-11,-16 0,-11 V17 Q-11,12 -22,17 Z" fill="{paper}" stroke="{ink}" stroke-width="2" stroke-linejoin="round"/>
<path d="M0,-11 Q11,-16 22,-11 V17 Q11,12 0,17 Z" fill="{paper}" stroke="{ink}" stroke-width="2" stroke-linejoin="round"/>
{left}{right}
<g transform="translate(19,-19)"><g>{xform('scale', ['.8', '1.3', '.8'], [0, .5, 1], dur=1.5)}
  <path d="{star}" fill="{hi}" stroke="{paper}" stroke-width="1.2" stroke-linejoin="round"/></g></g>"""
