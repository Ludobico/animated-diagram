# Drawing an icon in the house style

There is no catch-all icon. When `make_diagram.py` stops with `no icon for: ...`, or a guessed icon is
wrong, give each node a real icon:

1. **A core key that fits** (`references/icons.md`). Use it when the core icon shows the same idea,
   even if the product differs (an ERP or billing system can be a `server`; a LangGraph graph can be a
   `service-graph`).
2. **Otherwise draw one.** Every node gets a drawn icon with its own micro-interaction. That is the
   point of this skill, so drawing is expected, not a last resort. Abstract nodes ("logic",
   "processing") still get an icon: show what the node does (gears turning, items being sorted),
   not a letter or a placeholder.

## How

1. Pick the two core modules closest in form and read them, for example `scripts/icons/trace.py`
   for a panel, `database.py` for a container, or `queue.py` for a flow. Copy their proportions and
   motion; do not read the whole library.
2. Write one file per icon in the job's work folder (SKILL.md, "Files"), such as `<work>/payment.py`, in the
   core format. `examples/icons/learning.py` is a complete drawn example.

   ```python
   from icons._svg import anim, xform

   KEY = "payment"                       # lowercase kebab-case, not an existing key
   SHAPE = "card with a chip"
   MOTION = "card slides out, chip glints"


   def draw(p, uid="", label=""):
       ink, hi, paper = p["ink"], p["hi"], p["paper"]
       return f"""
   <rect x="-22" y="-14" width="44" height="28" rx="4" fill="{paper}" stroke="{ink}" stroke-width="2"/>
   ..."""
   ```
3. Set `"icon": "payment"` on the node and render with `--extra-icons <work>/payment.py`.
4. Preview: `preview_icon.py <work>/strip.png payment --extra-icons <work>/payment.py --theme both`.
   The shape must read at a glance on the light and the dark row, and the motion must visibly change
   across the 8 frames.
5. `check.py` must pass `ids`, `loop` and `icon` (it catches colours outside the palette and an icon
   that does not move).

## House style (measured from the core icons)

**Frame.** Draw centred on 0,0 within about +-26. The main silhouette is about 40-48 wide and 36-44 tall.
The node scales the icon, so use these numbers as they are.

**Layers and colours.** Use only the palette `p`. Never write a literal colour (`#fff` included): the
same file renders in both themes.

| Layer | Colour | Stroke | Core examples |
|---|---|---|---|
| Main silhouette | fill `paper`, stroke `ink` | 2, round joins; rect `rx` 3-11 | browser window, server rack, cloud, shield |
| Static detail (text rows, separators, pins) | `ink` | 1.4-1.8, `opacity` .45-.6 | trace rows, storage line, chip pins |
| Secondary surface | fill `tint`, stroke `ink` | 2 | cylinder top, plug socket, router hub |
| **Moving part** | `hi` | lines 2.2-2.6 with round caps; dots r 2-3.6 | server bars, chat-bot dots, queue boxes |
| Corner badge (optional) | sparkle in `hi`, or an `ink` disc with a `paper` glyph | — | terminal sparkle, service-graph bolt |

Motion lives on `hi` parts. `ink` parts stay still, apart from a whole-group transform or an
`ink`→`hi` highlight.

**Motion vocabulary.** Use one primary motion that acts out what the node does, plus at most one or
two small secondary motions. Core icons have 2-6 animated elements.

| Motion | SMIL | Period | Core examples |
|---|---|---|---|
| Blink | `opacity` 1 → .15 → 1 | 1.5 s | server LEDs, user dot, chat-bot antenna |
| Pulse | `r` or `scale` 1 → 1.15-1.4 → 1 | 1-1.5 s | cache bolt, database dot, llm star |
| Ring spread | outline copy: `r` +7, `opacity` .8 → 0 | 1.5-3 s | user, vector-db, key |
| Write / fill | `x2` or `width` grows, holds until .8-.9, snaps back | 3 s | server bars, terminal command, trace spans |
| Draw stroke | `stroke-dashoffset` 100 → 0 with `pathLength="100"` | 3 s | shield-check tick |
| Travel | `translate` or `animateMotion` along a path | 2-3 s | queue messages, router packets, storage file |
| Spin | `rotate` 0 → 360 | 3-6 s | poller arrows, browser atom |
| Highlight | `stroke` ink → hi → ink | 3 s | service-graph nodes |
| Sequence | the same motion on n parts, `begin` = -i × step | — | server rows, api dots, database rows |

**Timing.** Every period divides 6 s: 3 and 1.5 are the defaults; 1 and 1.2 for quick tics; 6 for
slow spins. Offsets are negative `begin` values, never positive ones.

**Ids.** Prefix every `id` with `uid` (`id="clip-{uid}"`), so two nodes with one icon do not collide.

**Avoid.** Letters or text, gradients, filters, blur or shadows, images or font glyphs, external icon
sets, product or company logos, dashed outlines (the node ring already uses them), strokes thicker
than about 3.4, and a shape that duplicates a core icon.

## Report and keep

- List each drawn icon in the result: node, key, shape, motion. Say that it was drawn for this job.
- Drawn icons are throwaway by default: the cleanup in SKILL.md step 5 deletes them with `<work>/`. If the
  user wants to keep one, copy it where they say before the cleanup. Add one to the core library only when
  the user asks: copy the
  file into `scripts/icons/`, add a keyword rule to `_RULES` in `scripts/icons/__init__.py` if it should
  be auto-selected, then run `python -m icons` from `scripts/` to regenerate `references/icons.md`.
