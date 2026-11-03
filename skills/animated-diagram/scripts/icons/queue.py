from icons._svg import anim, xform

KEY = "queue"
SHAPE = "pipe + messages"
MOTION = "message boxes flow through the pipe"


def draw(p, uid="", label=""):
    ink, hi = p["ink"], p["hi"]
    boxes = ""
    for i in range(3):
        boxes += (f'<g opacity="0">{anim("opacity", [0, 1, 1, 0], [0, .1, .85, 1], dur=2, begin=-2 * i / 3)}'
                  f'{xform("translate", ["-20 0", "20 0"], dur=2, begin=-2 * i / 3)}'
                  f'<rect x="-4.5" y="-5.5" width="9" height="11" rx="2" fill="{hi}"/></g>')
    return f"""
<line x1="-26" y1="-13" x2="26" y2="-13" stroke="{ink}" stroke-width="2.4" stroke-linecap="round"/>
<line x1="-26" y1="13" x2="26" y2="13" stroke="{ink}" stroke-width="2.4" stroke-linecap="round"/>
<polyline points="20,-7 26,0 20,7" fill="none" stroke="{ink}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" opacity=".6"/>
{boxes}"""
