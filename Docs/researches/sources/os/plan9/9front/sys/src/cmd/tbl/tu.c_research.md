# File Research: sources/os/plan9/9front/sys/src/cmd/tbl/tu.c

Draws horizontal rules and maintains line-stop metadata for `tbl`.

Key points:
- `makeline` expands a single cell rule into the full span of adjacent compatible rule cells, unless it is a short escaped rule.
- `fullwide` draws full-width top/bottom/all-table rules while skipping vertically spanned columns.
- `drawline` emits troff `\l` line-drawing commands, choosing one or two strokes for single/double rules and adjusting endpoints at vertical intersections.
- Handles printer-specific behavior for `pr1403` and line-size adjustments via `LSIZE`.
- `getstop` assigns line-stop registers used as vertical-line endpoints.
- `left` finds the start row and width of a vertical line segment at a column boundary.
- `lefdata` derives vertical-line style from explicit left-line style, box/double-box/all-line flags, and spans.
- `next` and `prev` skip full-rule/replacement rows while walking table data.

Dependencies and interactions:
- Calls `thish`, `ctype`, `interv`, `tohcol`, `reg`, `vspand`, `lefdata`, `prev`, and `next`.
- Feeds vertical-line drawing by populating `linestop`.

Research relevance:
- This is the core horizontal-line renderer and vertical-line segment discovery code.
