# /// script
# requires-python = ">=3.10"
# dependencies = ["pillow>=10", "playwright>=1.40"]
# ///
import os
import re
import sys
from io import BytesIO
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageFont
from playwright.sync_api import Error as PlaywrightError, sync_playwright

def launch(pw):
    # an installed Chrome, then Edge (bundled with Windows), then `playwright install chromium`
    forced = os.environ.get("BROWSER_CHANNEL")
    for channel in [forced] if forced else ["chrome", "msedge", None]:
        try:
            return pw.chromium.launch(channel=channel)
        except PlaywrightError:
            continue
    raise SystemExit("no browser found: install Chrome or Edge, or run `playwright install chromium`")

def capture(svg, fps, dur, scale):
    m = re.search(r'viewBox="[-\d.]+[\s,]+[-\d.]+[\s,]+([\d.]+)[\s,]+([\d.]+)"', svg.read_text(encoding="utf-8"))
    w, h = round(float(m[1])), round(float(m[2]))
    with sync_playwright() as pw:
        browser = launch(pw)
        page = browser.new_page(viewport={"width": w, "height": h}, device_scale_factor=scale)
        page.goto(svg.resolve().as_uri())
        page.evaluate("document.documentElement.pauseAnimations()")
        shots = []
        for i in range(round(fps * dur)):
            page.evaluate(f"document.documentElement.setCurrentTime({i / fps})")
            shots.append(page.screenshot())  # PNG bytes in memory, no frames/ folder
        browser.close()
    return shots

def indices(im):
    # palette indices as a grayscale image, so ImageChops can compare them
    return Image.frombytes("L", im.size, im.tobytes())


def encode(shots, out, fps, colors, width=None):
    def rgb(png):
        im = Image.open(BytesIO(png)).convert("RGB")
        if width and im.width != width:
            im = im.resize((width, round(im.height * width / im.width)), Image.Resampling.LANCZOS)
        return im

    # one palette for every frame (no colour flicker); the last slot is reserved for transparency
    sample = [rgb(s) for s in shots[:: max(1, len(shots) // 12)]]
    sheet = Image.new("RGB", (sample[0].width, sample[0].height * len(sample)))
    for i, im in enumerate(sample):
        sheet.paste(im, (0, im.height * i))
    palette = sheet.quantize(colors - 1, method=Image.Quantize.MAXCOVERAGE)
    clear = colors - 1
    rgb_table = palette.getpalette()[: 3 * clear] + [0, 0, 0]

    frames, prev = [], None
    for png in shots:
        cur = rgb(png).quantize(palette=palette, dither=Image.Dither.NONE)
        frame = cur.copy()
        if prev is not None:
            # a pixel equal to the previous frame becomes transparent and the GIF keeps the old one;
            # most of a diagram is static, so this cuts the file to about a quarter
            same = ImageChops.difference(indices(cur), indices(prev)).point(lambda v: 255 if v == 0 else 0)
            frame.paste(clear, mask=same)
        frame.putpalette(rgb_table)
        frames.append(frame)
        prev = cur
    frames[0].save(out, save_all=True, append_images=frames[1:], duration=round(1000 / fps),
                   loop=0, disposal=1, transparency=clear, optimize=False)


def contact_sheet(shots, out, fps):
    # out.png instead of out.gif: the frames in two columns, each stamped with its time, for a quick look
    ims = [Image.open(BytesIO(s)).convert("RGB") for s in shots]
    w, h = ims[0].size
    cols = min(2, len(ims))
    grid = Image.new("RGB", (w * cols, h * -(-len(ims) // cols)), ims[0].getpixel((0, 0)))  # canvas colour, dark or light
    draw = ImageDraw.Draw(grid)
    font = ImageFont.load_default(size=max(14, h // 30))
    for i, im in enumerate(ims):
        x, y = (i % cols) * w, (i // cols) * h
        grid.paste(im, (x, y))
        draw.text((x + w - 10, y + 8), f"t={i / fps:.2f}s", fill="#dc2626", font=font, anchor="ra")
    grid.save(out)

if __name__ == "__main__":
    if len(sys.argv) < 3:
        raise SystemExit("usage: capture.py in.svg out.gif|frames.png [fps=25] [seconds=6] [scale=1]")
    svg, out = Path(sys.argv[1]), Path(sys.argv[2])
    fps = float(sys.argv[3]) if len(sys.argv) > 3 else 25
    dur = float(sys.argv[4]) if len(sys.argv) > 4 else 6
    scale = float(sys.argv[5]) if len(sys.argv) > 5 else 1
    shots = capture(svg, fps, dur, scale)
    if out.suffix.lower() == ".png":
        contact_sheet(shots, out, fps)
    else:
        encode(shots, out, fps, int(os.environ.get("GIF_COLORS", 128)), int(os.environ.get("GIF_WIDTH", 0)))
    print(f"wrote {out}: {len(shots)} frames, {out.stat().st_size / 1048576:.2f}MB")
