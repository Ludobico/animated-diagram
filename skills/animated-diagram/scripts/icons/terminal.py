from icons._svg import anim, xform

KEY = "terminal"
SHAPE = "terminal window + sparkle"
MOTION = "command types out, cursor blinks, sparkle twirls"


def draw(p, uid="", label=""):
    paper = p["paper"]
    ink, hi = p["ink"], p["hi"]
    star = "M0,-7 Q0.8,-0.8 7,0 Q0.8,0.8 0,7 Q-0.8,0.8 -7,0 Q-0.8,-0.8 0,-7z"
    return f"""
<rect x="-24" y="-16" width="48" height="36" rx="5" fill="{paper}" stroke="{ink}" stroke-width="2"/>
<line x1="-24" y1="-7" x2="24" y2="-7" stroke="{ink}" stroke-width="2"/>
<circle cx="-18" cy="-11.5" r="1.4" fill="{ink}"/><circle cx="-13" cy="-11.5" r="1.4" fill="{ink}"/>
<polyline points="-17,1 -11,6 -17,11" fill="none" stroke="{hi}" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"/>
<line x1="-6" y1="6" x2="-6" y2="6" stroke="{hi}" stroke-width="2.4" stroke-linecap="round">
  {anim('x2', [-6, 8, 8, -6], [0, .45, .9, 1], dur=3)}
</line>
<rect x="12" y="4" width="6" height="4.4" rx="1" fill="{ink}">{anim('opacity', [1, 0], dur=1, discrete=True)}</rect>
<g transform="translate(21,-19)">
  <g>{xform('rotate', ['0','90'], dur=3)}
    <g>{xform('scale', ['.85','1.25','.85'], [0, .5, 1], dur=1.5)}
      <path d="{star}" fill="{hi}" stroke="{paper}" stroke-width="1.4" stroke-linejoin="round"/></g></g>
</g>"""
