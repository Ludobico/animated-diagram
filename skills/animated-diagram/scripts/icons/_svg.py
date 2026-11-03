"""SVG/SMIL helpers shared by every icon (core and --extra-icons)."""

T = 6.0


def n(x):
    s = f"{x:.2f}".rstrip("0").rstrip(".")
    return s if s else "0"


def kt(vals):
    return ";".join(n(v) if 0 < v < 1 else str(int(v)) for v in vals)


def anim(attr, values, keytimes=None, dur=T, begin=0.0, discrete=False):
    s = f'<animate attributeName="{attr}" values="{";".join(str(v) for v in values)}"'
    if keytimes:
        s += f' keyTimes="{kt(keytimes)}"'
    if discrete:
        s += ' calcMode="discrete"'
    s += f' dur="{n(dur)}s" begin="{n(begin)}s" repeatCount="indefinite"/>'
    return s


def xform(kind, values, keytimes=None, dur=T, begin=0.0, discrete=False):
    s = f'<animateTransform attributeName="transform" type="{kind}" values="{";".join(values)}"'
    if keytimes:
        s += f' keyTimes="{kt(keytimes)}"'
    if discrete:
        s += ' calcMode="discrete"'
    s += f' dur="{n(dur)}s" begin="{n(begin)}s" repeatCount="indefinite"/>'
    return s


def cylinder(p, uid, top=-14, bottom=16, rx=19, ry=6):
    return (f'<path d="M{-rx},{top} V{bottom} A{rx},{ry} 0 0 0 {rx},{bottom} V{top}" fill="{p["paper"]}" stroke="{p["ink"]}" stroke-width="2"/>'
            f'<clipPath id="cl-{uid}"><path d="M{-rx},{top} V{bottom} A{rx},{ry} 0 0 0 {rx},{bottom} V{top} Z"/></clipPath>')
