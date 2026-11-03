from icons._svg import anim

KEY = "chat-bot"
SHAPE = "speech bubble + antenna"
MOTION = "typing dots bounce, antenna blinks"


def draw(p, uid="", label=""):
    paper = p["paper"]
    ink, hi = p["ink"], p["hi"]
    dots = "".join(
        f'<circle cx="{x}" cy="-5" r="2.5" fill="{hi}">'
        f'{anim("cy", [-5, -9.5, -5, -5], [0, .25, .5, 1], dur=1.2, begin=-0.3 * i)}</circle>'
        for i, x in enumerate((-8, 0, 8))
    )
    return f"""
<g transform="translate(0,3)">
  <line x1="0" y1="-20" x2="0" y2="-26" stroke="{ink}" stroke-width="2" stroke-linecap="round"/>
  <circle cx="0" cy="-27.5" r="2.6" fill="{hi}">{anim('opacity', [1, .2, 1], [0, .5, 1], dur=1.5)}</circle>
  <path d="M-22,-12 a8,8 0 0 1 8,-8 h28 a8,8 0 0 1 8,8 v14 a8,8 0 0 1 -8,8 h-16 l-8,8 v-8 h-4 a8,8 0 0 1 -8,-8 z"
        fill="{paper}" stroke="{ink}" stroke-width="2" stroke-linejoin="round"/>
  {dots}
</g>"""
