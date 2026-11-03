from icons._svg import anim, xform

KEY = "plug"
SHAPE = "socket and plug"
MOTION = "plug slides in with a spark"


def draw(p, uid="", label=""):
    paper = p["paper"]
    ink, hi = p["ink"], p["hi"]
    return f"""
<line x1="-30" y1="0" x2="-22" y2="0" stroke="{ink}" stroke-width="2.4" stroke-linecap="round"/>
<rect x="-22" y="-12" width="16" height="24" rx="3" fill="{p['tint']}" stroke="{ink}" stroke-width="2"/>
<line x1="-12" y1="-5.5" x2="-8" y2="-5.5" stroke="{ink}" stroke-width="2" stroke-linecap="round"/>
<line x1="-12" y1="5.5" x2="-8" y2="5.5" stroke="{ink}" stroke-width="2" stroke-linecap="round"/>
<polyline points="-4,-8 -8,0 -3,0 -7,8" fill="none" stroke="{hi}" stroke-width="2" stroke-linejoin="round" stroke-linecap="round" opacity="0">
  {anim('opacity', [0, 0, 1, 0, 0], [0, .16, .2, .34, 1], dur=3)}
</polyline>
<g>{xform('translate', ['8 0','-2 0','-2 0','8 0','8 0'], [0, .2, .6, .8, 1], dur=3)}
  <rect x="6" y="-12" width="16" height="24" rx="3" fill="{paper}" stroke="{ink}" stroke-width="2"/>
  <line x1="6" y1="-5.5" x2="-4" y2="-5.5" stroke="{ink}" stroke-width="2.6" stroke-linecap="round"/>
  <line x1="6" y1="5.5" x2="-4" y2="5.5" stroke="{ink}" stroke-width="2.6" stroke-linecap="round"/>
  <line x1="22" y1="0" x2="30" y2="0" stroke="{ink}" stroke-width="2.4" stroke-linecap="round"/>
</g>"""
