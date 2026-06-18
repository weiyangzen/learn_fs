# File Research: sources/os/plan9/plan9/sys/src/cmd/tbl/ti.c

Classifies intersections between horizontal and vertical table rules.

Key functions:
- `interv` determines whether a vertical line crosses, starts, or ends at a horizontal rule position.
- `interh` determines whether a horizontal line crosses or meets vertical rules at a column boundary.
- `up1` finds the previous non-`instead` row.

Used by:
- `drawline` in `tu.c` for horizontal rule endpoint adjustments.
- `drawvert` in `tv.c` for vertical rule endpoint adjustments.

Notable behavior:
- Double boxes (`dboxflg`) force boundary intersections.
- Full horizontal rows and adjacent all-horizontal rows influence classification.
