from icons._svg import anim

KEY = "trace"
SHAPE = "trace waterfall"
MOTION = "span bars grow in sequence"


def draw(p, uid="", label=""):
    paper = p["paper"]
    ink, hi = p["ink"], p["hi"]
    spans = [(-17, 28), (-11, 20), (-5, 26), (3, 14)]
    rows = ""
    for i, (x, w) in enumerate(spans):
        y = -9 + i * 7
        s, e = 0.02 + 0.06 * i, 0.1 + 0.06 * i
        rows += (f'<rect x="{x}" y="{y}" width="0" height="4.2" rx="2.1" fill="{hi if i % 2 == 0 else ink}">'
                 f'{anim("width", [0, 0, w, w, 0], [0, s, e, 0.9, 1], dur=3)}</rect>')
    return f"""
<rect x="-24" y="-18" width="48" height="38" rx="5" fill="{paper}" stroke="{ink}" stroke-width="2"/>
<line x1="-24" y1="-13" x2="24" y2="-13" stroke="{ink}" stroke-width="1.6" opacity=".6"/>
<circle cx="-19" cy="-15.6" r="1.1" fill="{ink}"/><circle cx="-15.5" cy="-15.6" r="1.1" fill="{ink}"/>
{rows}
<line x1="-19" y1="-11" x2="-19" y2="18" stroke="{ink}" stroke-width="1.2" stroke-dasharray="2 2" opacity=".4"/>"""
