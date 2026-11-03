from icons._svg import anim

KEY = "api"
SHAPE = "{ } braces"
MOTION = "dots light up in turn"


def draw(p, uid="", label=""):
    ink, hi = p["ink"], p["hi"]
    dots = "".join(
        f'<circle cx="{x}" cy="0" r="2.6" fill="{hi}">{anim("opacity", [.25, 1, .25, .25], [0, .2, .45, 1], dur=1.5, begin=-0.2 * i)}</circle>'
        for i, x in enumerate((-8, 0, 8)))
    return f"""
<path d="M-8,-16 Q-17,-16 -17,-7 V-4 Q-17,0 -22,0 Q-17,0 -17,4 V7 Q-17,16 -8,16" fill="none" stroke="{ink}" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"/>
<path d="M8,-16 Q17,-16 17,-7 V-4 Q17,0 22,0 Q17,0 17,4 V7 Q17,16 8,16" fill="none" stroke="{ink}" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"/>
{dots}"""
