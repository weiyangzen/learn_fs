# File Research: sources/os/plan9/plan9/sys/src/cmd/abaco/tabs.c

HTML table sizing, row/column fixing, and table layout for Abaco.

Key responsibilities:
- Draws table boxes by drawing contained cell layouts.
- Initializes table cell layout metadata.
- Computes cell widths and heights, including spans and separators.
- Distributes table widths across fixed, percentage, and flexible dimensions.
- Computes row heights and total table height.
- Sizes a table for available width.
- Lays out table cells into rectangles and creates per-cell `Lay` structures.

Dependencies:
- Uses libhtml `Table`, `Tablecell`, `Itable`, and `Dimen`.
- Calls `layitems`, `laydraw`, `dimwidth`, `frdims`, and drawing helpers.

Notable risks:
- Column/row span calculations are compact and sensitive to malformed tables.
- Table width allocation uses heuristic distribution rather than full browser layout rules.
