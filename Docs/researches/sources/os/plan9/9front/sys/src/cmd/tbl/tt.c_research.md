# File Research: sources/os/plan9/9front/sys/src/cmd/tbl/tt.c

Provides helpers for table style lookup, spanning, and horizontal-rule classification.

Key points:
- `ctype` maps a data row and column to the active style character, suppressing replacement/full-rule rows.
- `fspan`, `lspan`, and `ctspan` identify horizontal span relationships.
- `tohcol` emits troff horizontal movement to a column boundary or midpoint between adjacent columns.
- `allh` returns true when a row is entirely horizontal-rule content and contains at least one real rule.
- `thish` classifies a cell as no rule, empty, single rule, double rule, or vertically spanned placeholder; it follows spans leftward and recognizes `_`, `=`, and escaped rule entries.

Dependencies and interactions:
- Uses `table`, `style`, `stynum`, `fullbot`, `ncol`, `nlin`, and helpers `reg`, `point`, `vspen`, and `barent`.
- Called heavily by horizontal/vertical line drawing.

Research relevance:
- This file is the rule/spanning query layer used by the renderer.
