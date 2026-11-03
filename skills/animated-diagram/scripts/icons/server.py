from icons._svg import anim

KEY = "server"
SHAPE = "three-unit server rack"
MOTION = "LEDs blink, activity bars sweep"


def draw(p, uid="", label=""):
    paper = p["paper"]
    ink, hi = p["ink"], p["hi"]
    rows = ""
    for i, y in enumerate((-18, -3, 12)):
        rows += (f'<rect x="-22" y="{y}" width="44" height="12" rx="3" fill="{paper}" stroke="{ink}" stroke-width="2"/>'
                 f'<circle cx="-15" cy="{y + 6}" r="2" fill="{hi}">{anim("opacity", [1, .15, 1], [0, .5, 1], dur=1.5, begin=-0.5 * i)}</circle>'
                 f'<line x1="-6" y1="{y + 6}" x2="16" y2="{y + 6}" stroke="{ink}" stroke-width="1.6" stroke-linecap="round" opacity=".45"/>'
                 f'<line x1="-6" y1="{y + 6}" x2="-6" y2="{y + 6}" stroke="{hi}" stroke-width="2.4" stroke-linecap="round">'
                 f'{anim("x2", [-6, 16, 16, -6], [0, .4, .8, 1], dur=3, begin=-1 * i)}</line>')
    return rows
