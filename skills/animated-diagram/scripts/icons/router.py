from icons._svg import anim, n

KEY = "router"
SHAPE = "one-to-three router"
MOTION = "packets route to the three outputs in turn, hub pulses"


def draw(p, uid="", label=""):
    paper = p["paper"]
    ink, hi = p["ink"], p["hi"]
    outs = [(22, -15), (22, 0), (22, 15)]
    lanes, dots = "", ""
    for i, (x, y) in enumerate(outs):
        d = f"M-26,0 L-9,0 C0,0 4,{y} 14,{y} L{x - 3},{y}"
        lanes += f'<path d="{d}" fill="none" stroke="{ink}" stroke-width="2" stroke-linecap="round" opacity=".35"/>'
        lanes += (f'<path d="{d}" fill="none" stroke="{hi}" stroke-width="2.6" stroke-linecap="round" opacity="0">'
                  f'{anim("opacity", [0, 1, 1, 0, 0], [0, .08, .3, .36, 1], dur=3, begin=-(3 - i))}</path>')
        lanes += f'<circle cx="{x}" cy="{y}" r="3.6" fill="{paper}" stroke="{ink}" stroke-width="2"/>'
        dots += (f'<circle r="3.2" fill="{hi}" stroke="{paper}" stroke-width="1.2" opacity="0">'
                 f'<animateMotion dur="3s" begin="{n(-(3 - i))}s" repeatCount="indefinite" path="{d}" keyPoints="0;1;1" keyTimes="0;.33;1" calcMode="linear"/>'
                 f'{anim("opacity", [1, 1, 0, 0], [0, .33, .34, 1], dur=3, begin=-(3 - i))}</circle>')
    return f"""
{lanes}
<circle r="7" fill="{p['tint']}" stroke="{ink}" stroke-width="2"/>
<circle r="2.6" fill="{ink}">{anim('r', [2.6, 3.6, 2.6], [0, .5, 1], dur=1.0)}</circle>
{dots}"""
