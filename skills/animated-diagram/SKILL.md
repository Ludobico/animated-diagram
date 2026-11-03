---
name: animated-diagram
description: >-
  Animate an architecture diagram (Mermaid, text or image) as a GIF/SVG with icon micro-interactions
  and flowing data packets. Use for "animate this diagram".
---

# Animated Diagram

```
Mermaid ──mermaid_to_spec.py──┐
text / image ──(you extract)──┴─▶ spec.json ─make_diagram.py─▶ animated SVG ─check.py─▶ capture.py ─▶ GIF
```

It draws structure, not message order or step-by-step state changes; a sequence diagram can be redrawn
as its structure (step 2). Input: Mermaid flowchart code, a plain-text description of components and
connections, or an image of a diagram (screenshot, photo, whiteboard).

Scripts are in `${CLAUDE_SKILL_DIR}/scripts/`. If that text appears literally (outside Claude Code),
it means the folder you read this SKILL.md from. Write every output to the user's working directory
(in a cloud sandbox, the outputs folder), never into the skill folder.

**Setup.** Python 3.10+. `mermaid_to_spec.py`, `make_diagram.py` and `check.py` use only the standard
library. `capture.py` and `preview_icon.py` need Pillow and Playwright: run them with `uv run`, which
installs both into a cached environment. Without uv, run `pip install pillow playwright` and use `python`.
They use an installed Chrome or Edge; if neither exists, run `playwright install chromium` once. If no
browser can be installed (for example, a sandbox that cannot reach the download), deliver the animated
SVG, which plays in browsers and READMEs, and say that the GIF could not be made there.

## 1. Settle line style and theme (one question)

Nothing in the input decides these two; they depend on taste and where the GIF will be shown.

- If the user stated or clearly implied a choice ("connected from the start", "for our dark-mode
  docs"), follow it. Do not infer from weak hints.
- Otherwise ask with **one** AskUserQuestion call holding both questions (where that tool does not
  exist, ask both in one message). Mark no option as recommended.
  - Lines: "Connected from the start" → `--lines static` (lines, arrowheads and labels always visible;
    only packets move), or "Lines draw themselves" → `--lines draw` (lines draw on, fade, repeat every 6 s).
  - Theme: "Light" → `--theme light`, "Dark" → `--theme dark`, or "Both (README switches with the
    viewer's mode)" → render both and give the `<picture>` snippet from step 4.
- For text or image input, put this in the same call as the spec confirmation of step 2, so the user
  answers once.
- Ask once per job, even for several diagrams; reuse the answers for later revisions of the same job.
- If you cannot ask (non-interactive run), use `draw` and `light`, and say so in the report.

## 2. Build the spec

- **Mermaid** (`flowchart`/`graph`):
  `python ${CLAUDE_SKILL_DIR}/scripts/mermaid_to_spec.py in.mmd spec.json` (use `-` to read stdin).
  A `sequenceDiagram` is not converted. Rewrite it as a flowchart: participants become nodes and
  messages become edges, as `examples/mermaid-architecture.mmd` does. Tell the user what you left out
  (message order, self-calls, alt/opt blocks).
- **Text or image**: write `spec.json` yourself, following these rules:
  1. Copy labels exactly. Do not translate, shorten or correct them. For a multi-line label, the first
     line is `label` and the rest is `sub`.
  2. Do not invent nodes or edges, and do not add components the input lacks.
  3. Arrow direction is data direction. Split a two-way arrow into two edges. If a direction is
     unclear, ask the user; do not guess.
  4. Groups follow the boxes, lanes or colours in the input. If the input has none, group by role
     (Clients / Services / Data) and tell the user the groups are your guess.
  5. Do not fill in unreadable text or ambiguous links. Point to them and ask.
  6. Count nodes and edges against the input. For an image, count the arrows one by one.
  7. If anything was inferred or hard to read, show the node and edge list and get a yes before rendering.

A Mermaid diagram without `subgraph` lands in one untitled group (one column). Group by role instead,
and say that the grouping is inferred. Past about 25 nodes, 7 per column or 6 columns, suggest
splitting the diagram.

```json
{
  "title": "RAG Chatbot",
  "optimize_order": true,
  "groups": [{ "id": "users", "title": "Users", "color": "purple" }],
  "nodes": [
    {
      "id": "web",
      "group": "users",
      "label": "Web App",
      "sub": "Next.js",
      "icon": "browser"
    }
  ],
  "edges": [{ "from": "web", "to": "gw", "label": "request" }]
}
```

| Field            | Notes                                                                                                                                                                      |
| ---------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `groups[]`       | Required. The array order is the left-to-right column order. `color`: purple, blue, green, orange, teal, rose, slate (cycles if omitted)                                   |
| `nodes[]`        | Required. `group` is a group id. Optional: `sub`, `icon` (guessed from the label if omitted), `size` sm/md/lg (by degree if omitted), `shape: "cylinder"` (datastore hint) |
| `edges[]`        | `from` → `to`, optional `label`. No self loops                                                                                                                             |
| `optimize_order` | `true` reorders nodes inside a column to reduce crossings                                                                                                                  |

Worked examples: `${CLAUDE_SKILL_DIR}/examples/`. `mermaid-architecture.mmd` → `.json` is the converter
output plus `icon` on the two nodes no keyword matched: one core key, and one drawn icon
(`examples/icons/learning.py`). `text-rag-chatbot.json` keeps its source text in `_comment`.

## 3. Render, check, look

```
python ${CLAUDE_SKILL_DIR}/scripts/make_diagram.py spec.json out.svg --lines static|draw --theme light|dark [--extra-icons my_icon.py ...]
python ${CLAUDE_SKILL_DIR}/scripts/check.py out.svg
uv run ${CLAUDE_SKILL_DIR}/scripts/capture.py out.svg frames.png 0.5 6
```

- **Icons**: every node needs a real icon; there is no placeholder. Keywords pick one where they can, and
  `make_diagram.py` prints each choice. If it stops with `no icon for: ...`, or a guess is wrong, set
  `"icon"` to a fitting core key (`references/icons.md`) or draw one in the house style of the core
  icons (`references/custom-icons.md`).
- **Check**: fix every `FAIL` and render again. The usual fixes are node order, `size`, grouping, or
  splitting the diagram. A `warn` (crossing, an edge under a label) can stay, but mention it in the report.
  Known layout limits are in `references/limits.md`.
- **Look**: open `frames.png` (frames at 0, 2 and 4 s). Check for misleading icons, clipped labels, and
  lines over nodes. With `static`, the first frame must already show every line, arrowhead and label.

## 4. Capture the GIF

```
uv run ${CLAUDE_SKILL_DIR}/scripts/capture.py out.svg out.gif 25 6
```

The arguments are fps and seconds; keep the seconds at 6, the loop length. Optional environment
variables: `GIF_WIDTH=960` (resize), `GIF_COLORS=128`. Diagrams of 6–11 nodes came out at 0.7–1.3 MB.

For "Both", render and check each theme (`out-light.svg`, `out-dark.svg`), capture both GIFs, and give
the user this README snippet:

```html
<picture>
  <source media="(prefers-color-scheme: dark)" srcset="out-dark.gif" />
  <img src="out-light.gif" alt="architecture diagram" />
</picture>
```

## 5. Report

- Output paths and file sizes, and the line style and theme used (say if they were defaults).
- What you verified (check results, frames you looked at) and what you did not (for example, you did not
  watch the whole GIF).
- Anything you inferred: grouping, icon choices, readings of unclear text or arrows.
- New icons you drew (node, key, shape, motion), noting that they were made for this job only.
- Remaining limits or warnings, such as an unavoidable crossing.

## References

- `references/icons.md`: icon keys, shapes, motions, and auto-selection keywords.
- `references/custom-icons.md`: when and how to draw a missing icon, and how to check it.
- `references/limits.md`: layout behaviour, limits, Mermaid syntax, and verified scope.
- `references/design-notes.md`: timeline, loop seams, and encoding, for changing the scripts.
