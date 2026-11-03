from icons._svg import anim, xform

KEY = "storage"
SHAPE = "folder + file"
MOTION = "file drops into the folder"


def draw(p, uid="", label=""):
    paper = p["paper"]
    ink, hi = p["ink"], p["hi"]
    return f"""
<g>{xform('translate', ['0 -12', '0 0', '0 0'], [0, .6, 1], dur=1.5)}{anim('opacity', [0, 1, 1], [0, .4, 1], dur=1.5)}
  <path d="M-6,-14 h9 l5,5 v14 h-14 z" fill="{p['tint']}" stroke="{hi}" stroke-width="1.8" stroke-linejoin="round"/></g>
<path d="M-23,-6 h13 l4,5 h29 a2,2 0 0 1 2,2 v18 a3,3 0 0 1 -3,3 h-42 a3,3 0 0 1 -3,-3 z" fill="{paper}" stroke="{ink}" stroke-width="2" stroke-linejoin="round"/>
<line x1="-18" y1="9" x2="2" y2="9" stroke="{ink}" stroke-width="1.6" stroke-linecap="round" opacity=".45"/>"""
