from icons._svg import anim, cylinder

KEY = "vector-db"
SHAPE = "cylinder + vector points"
MOTION = "search ring spreads, nearest neighbours link up"


def draw(p, uid="", label=""):
    ink, hi = p["ink"], p["hi"]
    dots = [(-10, 1), (-3, 7), (7, 3), (11, 9), (-11, 10), (4, 11), (-5, -3)]
    q = (1, 3)
    nn = [(-3, 7), (7, 3), (-5, -3)]
    dd = "".join(f'<circle cx="{x}" cy="{y}" r="1.9" fill="{ink}"/>' for x, y in dots)
    lines = "".join(
        f'<line x1="{q[0]}" y1="{q[1]}" x2="{x}" y2="{y}" stroke="{hi}" stroke-width="1.2" stroke-dasharray="2 2">'
        f'{anim("opacity", [0, 1, 1, 0, 0], [0, .15, .6, .75, 1], dur=1.5, begin=-0.1 * i)}</line>'
        for i, (x, y) in enumerate(nn)
    )
    return f"""
{cylinder(p, uid)}
<g clip-path="url(#cl-{uid})">
  {lines}{dd}
  <circle cx="{q[0]}" cy="{q[1]}" r="2.6" fill="{hi}"/>
  <circle cx="{q[0]}" cy="{q[1]}" r="3" fill="none" stroke="{hi}" stroke-width="1.6">
    {anim('r', [3, 15], [0, 1], dur=1.5)}{anim('opacity', [.9, 0], [0, 1], dur=1.5)}</circle>
</g>
<ellipse cx="0" cy="-14" rx="19" ry="6" fill="{p['tint']}" stroke="{ink}" stroke-width="2"/>"""
