# File Research: sources/os/plan9/plan9/sys/src/cmd/tbl/tt.c

Helpers for span and horizontal-line classification.

Key functions:
- `ctype` returns active format style for a row/column, ignoring full horizontal rows and troff-control rows.
- `fspan`, `lspan`, and `ctspan` compute span relationships.
- `tohcol` emits horizontal movement to a column boundary.
- `allh` determines whether an entire row is horizontal rules.
- `thish` returns horizontal rule type for a cell: none, single, double, span continuation, or content-derived rule.

Notable behavior:
- `thish` treats empty cells and vertical spans as neutral/continuation.
- `barent` from `tv.c` is used to treat literal `_`/`=` entries as rule entries.
