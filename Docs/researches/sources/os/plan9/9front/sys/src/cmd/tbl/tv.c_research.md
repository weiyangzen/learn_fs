# File Research: sources/os/plan9/9front/sys/src/cmd/tbl/tv.c

Draws vertical table rules.

Key points:
- `drawvert` emits troff `\L` vertical line commands from a start row to an end row at column boundary `c`.
- Handles single and double vertical rules by drawing multiple offset strokes.
- Adjusts top and bottom endpoints based on adjacent horizontal rules, full bottom rules, all-horizontal rows, and intersection classifications.
- Uses `linestop` registers and string `#d` to account for normal versus diversion vertical position.
- `midbar` and `midbcol` detect whether a horizontal bar crosses the vertical line boundary.
- `barent` recognizes cell strings that encode `_` or `=` rule entries, including escaped forms.

Dependencies and interactions:
- Calls `interh`, `midbar`, `midbcol`, `barent`, `allh`, `ctype`, and `point`.
- Consumes line stops created by `getstop`.

Research relevance:
- Complements `tu.c` by rendering vertical borders and separators with correct intersections.
