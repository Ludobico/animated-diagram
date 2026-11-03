# Design notes

Background for changing the scripts. Not needed for normal use.

- **Timeline (6 s, `draw`)**: 0.2-1.8 s connectors draw on in order. Then the arrowhead appears, and
  packets (a dot with a tail) run along the path and ripple on arrival. At 5.5-6.0 s the connectors
  fade out and the loop resets. Nodes and icons stay visible throughout.
- **`static`**: no draw-on, no fade-in and no fade-out. With no reset at the loop end, each packet
  period snaps to 1.5, 2, 3 or 6 s (whichever is nearest the length-based value) so the loop has no seam.
- **Loop seam**: every repeating period divides 6 s. Phase offsets are negative `begin` values. A
  positive `begin` leaves the element idle at the start; for `animateMotion` it also parks the element
  at the SVG origin until it starts. `check.py` fails both cases.
- **Arrowheads are `<polygon>`s, not markers**: a `marker` would show at the line end while the line is
  still drawing on. The polygon appears when drawing finishes.
- **Two-way pairs**: the edges run one port gap apart, which is narrower than a 28 px label pill. So
  their labels walk from the sender until the pill clears the edge start (`label_t` in `make_diagram.py`).
- **Frame capture**: `pauseAnimations()` and then `setCurrentTime(t)` for each frame. This is
  deterministic and drops no frames, unlike recording in real time.
- **GIF encoding** (Pillow, no ffmpeg): one 127-colour MAXCOVERAGE palette from about 12 sampled frames,
  plus one transparent slot. A pixel that matches the previous frame becomes transparent
  (`disposal=1`). On an 11-node diagram: 1.24 MB, against 1.42 MB from ffmpeg and 4.6 MB without the
  frame diff.
- **Themes**: `THEMES` in `make_diagram.py` holds the canvas, `paper`, text colours and seven group
  palettes for `light` and `dark`. Icons only see the group palette plus `paper`, so one icon file serves
  both themes. Dark uses GitHub's dark background (`#0d1117`) and was tuned so that every pair is at
  least as readable as in light (WCAG contrast): labels 16:1, sub-labels 6.2:1, edge-label text on its
  pill 7.2–9.6:1, icon outline on the node face 9–11:1. Edge lines stay deliberately soft in both
  themes (light 1.4–1.7:1, dark 1.9–2.4:1); packets and arrowheads carry the colour.
- **Fonts**: `font-family` lists Pretendard, Segoe UI, Malgun Gothic, Noto Sans KR and Apple SD Gothic
  Neo. A GIF bakes in the fonts of the machine that rendered it; an animated SVG uses the viewer's fonts.
- **README use**: `![architecture](assets/architecture.gif)`. For sharper text, embed the animated SVG
  with `<img src="assets/architecture.svg">`. Chat apps, email and slides often show only the first frame
  of an SVG, so ship the GIF too.
- **Collision fixes** (from the original fireworks checks): edge starts sit 4.9 px outside the port dot,
  and ends sit 9.6 px before the arrowhead base. This keeps lines from touching circles and arrowheads.
