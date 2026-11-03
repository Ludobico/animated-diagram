# Layout, limits and verified scope

## How the layout works

- Each group is one vertical column; columns run left to right in `groups[]` order. Nodes spread
  evenly down their column.
- Edges between columns are Beziers with horizontal tangents. Adjacent nodes in one column get a
  vertical line; non-adjacent nodes in one column get a curve that bulges out to the right.
  Right-to-left (reverse) edges are supported.
- Several edges on one side of a node get separate ports (up to `--port-gap` px apart, default 10).
- Edge labels sit at the edge midpoint. When both edges of a two-way pair (A->B and B->A) have a
  label, each label moves toward the node that sends it, so the two do not stack.
- `optimize_order: true` reorders nodes inside a column to cut crossings and lifts a producer above
  the node it feeds in the same column.

## Limits

| Limit | Detail |
|---|---|
| Top-down diagrams | Direction is ignored; the layout is always left-to-right columns (`mermaid_to_spec.py` warns on `TD`/`TB`/`BT`) |
| Crossings | Not always avoidable: two sources that both feed the same two targets (2x2) cross at least once. `check.py` warns |
| Column-skipping edges | An edge from column 1 to column 3 can pass over a node in column 2. `check.py` fails `edge_node` |
| Size | Readability drops past about 7 nodes per column, 25 nodes, or 5-6 columns. Largest verified: 11 nodes, 4 columns. Suggest splitting bigger diagrams |
| Self loops | Not supported (spec validation error) |
| Nested groups | Mermaid nested subgraphs keep only the innermost box |
| Nodes without a group | Go into an untitled group `main`, which stacks everything in one column |
| Free placement | Boxes inside boxes, arbitrary coordinates, or reproducing positions from a photo are not supported |
| Same-column pairs | A->B and B->A between adjacent nodes in one column share one vertical line; keep only one |

## Mermaid support (`mermaid_to_spec.py`)

`flowchart` / `graph` only. Supported: `subgraph`, node shapes `[] () ([]) [()] (()) {{}} {} >]`
(`[()]` becomes `shape: "cylinder"`), quoted labels, `<br/>` (first line `label`, rest `sub`),
`-->` `---` `-.->` `==>`, `|label|` and `-- label -->`, chains `A --> B --> C`, `A & B --> C`.
Ignored: `style`, `classDef`, `click`, `%%` comments. Not supported: `sequenceDiagram`, `classDiagram`
and other Mermaid diagram types. A sequence diagram can be rewritten by hand as a flowchart
(see the header of `examples/mermaid-architecture.mmd`).

## Verified so far

- `examples/mermaid-architecture.mmd` (a sequence diagram rewritten as a flowchart), 6 nodes / 8 edges /
  4 columns: convert, render, check with no warnings, GIF (0.86 MB).
- Mermaid, 11 nodes / 11 edges / 3 columns (an earlier private diagram): convert, render, check, GIF.
  One unavoidable 2x2 crossing.
- The same sequence diagram expanded to 11 nodes (graph steps as nodes) could not pass `edge_node` in
  any column order: `main.py` feeds both graphs and both write to the playbook, so one edge must skip a
  column and runs over a node. This is the column-skipping limit above.
- Text-extracted spec, 10 nodes / 10 edges / 4 columns, with reverse edges, edge labels and a vertical
  line: render, check, GIF.
- 6-node auth diagram with a labelled two-way pair: render, check, GIF.
- All 22 core icons as filmstrips, in both themes.
- Dark theme: the playbook example and the RAG text example render, pass `check.py`, and capture to GIF.
- Windows with Chrome and Edge.

Not verified:
- Photo or screenshot input: nothing automated reads the image; misreads are possible.
- Different inputs (Mermaid, text, image) of the same system are not guaranteed to yield the same spec.
- macOS and Linux rendering, and Playwright's bundled Chromium.
- Full playback of finished GIFs end to end; checks used representative frames.
