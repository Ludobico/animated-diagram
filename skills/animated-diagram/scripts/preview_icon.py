# /// script
# requires-python = ">=3.10"
# dependencies = ["pillow>=10", "playwright>=1.40"]
# ///
"""Filmstrip of icons, to eyeball shapes and micro-interactions before using them.

    python preview_icon.py out.png KEY [KEY ...] [--extra-icons my_icon.py ...] [--theme light|dark|both]
                           [--frames 8] [--span 3] [--color purple]

Rows are icons drawn on a node medallion, columns are moments spread over `span` seconds.
The default 8 frames over 3 s (0.375 s apart) never catch a 1, 1.2, 1.5, 2 or 3 s loop in the
same phase twice in a row, so a frozen or jumping animation is visible. `--theme both` stacks the
light strip over the dark one, so an icon that hard-codes a colour stands out.
"""
import argparse
from io import BytesIO
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont
from playwright.sync_api import sync_playwright

from capture import launch
from icons import ICONS, load_extra, n
from make_diagram import AUTO_COLORS, FONT, THEMES, esc, medallion, palette

R, SCALE, CELL_W, CELL_H = 64, 1.8, 180, 190


def sheet(keys, theme, color):
    """One column of icons, each on a node-style medallion with its key underneath."""
    th, p = THEMES[theme], palette(theme, color)
    h = CELL_H * len(keys)
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {CELL_W} {h}" width="{CELL_W}" height="{h}" font-family="{FONT}">',
           f'<rect width="{CELL_W}" height="{h}" fill="{th["bg"]}"/>']
    for i, key in enumerate(keys):
        cx, cy = CELL_W / 2, CELL_H * i + 82
        out.append(f'<g id="node-{esc(key)}" transform="translate({n(cx)},{n(cy)})">'
                   f'{medallion(R, SCALE, p, ICONS[key](p, f"pv{i}", key))}</g>'
                   f'<text x="{n(cx)}" y="{n(cy + R + 30)}" text-anchor="middle" font-size="16" font-weight="700" fill="{th["text"]}">{esc(key)}</text>')
    out.append("</svg>")
    return "\n".join(out), h


def filmstrip(svg_text, h, times, tmp, bg, scale=1):
    tmp.write_text(svg_text, encoding="utf-8")
    shots = []
    with sync_playwright() as pw:
        browser = launch(pw)
        page = browser.new_page(viewport={"width": CELL_W, "height": h}, device_scale_factor=scale)
        page.goto(tmp.resolve().as_uri())
        page.evaluate("document.documentElement.pauseAnimations()")
        for t in times:
            page.evaluate(f"document.documentElement.setCurrentTime({t})")
            shots.append(Image.open(BytesIO(page.screenshot())).convert("RGB"))
        browser.close()
    tmp.unlink()
    head = 28 * scale
    w, ih = shots[0].size
    strip = Image.new("RGB", (w * len(shots), ih + head), bg)
    draw = ImageDraw.Draw(strip)
    font = ImageFont.load_default(size=14 * scale)
    for i, (t, im) in enumerate(zip(times, shots)):
        strip.paste(im, (i * w, head))
        draw.text((i * w + w / 2, head / 2), f"t={t:.2f}s", fill="#8b949e", font=font, anchor="mm")
    return strip


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="icon filmstrip")
    ap.add_argument("out")
    ap.add_argument("keys", nargs="+", metavar="KEY")
    ap.add_argument("--extra-icons", nargs="+", default=[], metavar="FILE")
    ap.add_argument("--theme", choices=sorted(THEMES) + ["both"], default="light")
    ap.add_argument("--frames", type=int, default=8)
    ap.add_argument("--span", type=float, default=3.0, help="seconds covered by the frames")
    ap.add_argument("--color", choices=AUTO_COLORS, default="purple")
    args = ap.parse_args()
    for f in args.extra_icons:
        load_extra(f)
    unknown = [k for k in args.keys if k not in ICONS]
    if unknown:
        raise SystemExit(f"unknown icon {unknown}; choose from {sorted(ICONS)}")
    out = Path(args.out)
    times = [args.span * i / args.frames for i in range(args.frames)]
    strips = []
    for theme in (["light", "dark"] if args.theme == "both" else [args.theme]):
        svg_text, h = sheet(args.keys, theme, args.color)
        strips.append(filmstrip(svg_text, h, times, out.with_suffix(".preview.svg"), THEMES[theme]["bg"]))
    stacked = Image.new("RGB", (strips[0].width, sum(s.height for s in strips)))
    for i, s in enumerate(strips):
        stacked.paste(s, (0, sum(x.height for x in strips[:i])))
    stacked.save(out)
    print(f"wrote {out}: {len(args.keys)} icons x {len(times)} frames, theme={args.theme}")
