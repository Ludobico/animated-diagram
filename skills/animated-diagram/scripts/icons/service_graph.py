from icons._svg import anim

KEY = "service-graph"
SHAPE = "node graph + lightning badge"
MOTION = "token walks the graph, nodes light up in turn, badge pulses"


def draw(p, uid="", label=""):
    paper = p["paper"]
    ink, hi = p["ink"], p["hi"]
    nodes = [(-18, 9), (-6, -14), (14, -10), (20, 12), (2, 6)]
    links = [(0, 1), (1, 2), (2, 3), (0, 4), (4, 2), (4, 3), (1, 4)]
    ls = "".join(
        f'<line x1="{nodes[a][0]}" y1="{nodes[a][1]}" x2="{nodes[b][0]}" y2="{nodes[b][1]}" stroke="{ink}" stroke-width="1.8" stroke-linecap="round" opacity=".55"/>'
        for a, b in links
    )
    cs = "".join(
        f'<circle cx="{x}" cy="{y}" r="4.6" fill="{paper}" stroke="{ink}" stroke-width="2">'
        f'{anim("stroke", [ink, hi, ink, ink], [0, .1, .25, 1], dur=3, begin=0.6 * i - 3)}</circle>'
        for i, (x, y) in enumerate(nodes[:4])
    )
    e = nodes[4]
    cs += f'<circle cx="{e[0]}" cy="{e[1]}" r="4.6" fill="{paper}" stroke="{ink}" stroke-width="2"/>'
    path = "M-18,9 L-6,-14 L14,-10 L20,12 L2,6 Z"
    return f"""
<g transform="translate(0,2)">
  {ls}{cs}
  <circle r="3.3" fill="{hi}" stroke="{paper}" stroke-width="1.2">
    <animateMotion dur="3s" repeatCount="indefinite" path="{path}"/></circle>
</g>
<g transform="translate(22,-24)">
  <circle r="9.5" fill="{ink}" stroke="{paper}" stroke-width="2">{anim('r', [9.5, 10.8, 9.5], [0, .5, 1], dur=1.5)}</circle>
  <path d="M1.8,-6 L-3.4,1.2 H-0.2 L-1.6,6 L3.8,-1.4 H0.6 Z" fill="{paper}"/>
</g>"""
