# File Research: sources/os/plan9/plan9/sys/src/cmd/tbl/tv.c

Draws vertical table rules and identifies midline intersections.

Key functions:
- `drawvert` emits troff `\L` vertical line escapes from start to end rows, with endpoint adjustments for horizontal line intersections, double lines, printer mode, and diversions.
- `midbar` checks current or previous column for a horizontal rule crossing a vertical boundary.
- `midbcol` resolves spans and returns cell horizontal rule type.
- `barent` recognizes single-character `_`/`=` rule entries, accounting for optional leading backslash.

Notable behavior:
- Vertical drawing depends on `linestop` registers created by `getstop`.
- `barent(nil)` returns `1`, making missing data a neutral line continuation case.
