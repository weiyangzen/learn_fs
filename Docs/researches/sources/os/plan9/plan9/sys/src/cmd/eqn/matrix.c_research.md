# File Research: sources/os/plan9/plan9/sys/src/cmd/eqn/matrix.c

Matrix column assembly for `eqn`.

Key behavior:
- `startcol()` reserves entries in `lp[]` for a column and returns its start offset.
- `column()` records column type, entry count, and separation.
- `matrix()` converts multiple column boxes into a matrix, using tuned inter-column spacing and `eqnbox()` concatenation.

Filesystem relevance:
- Typesetting layout only.
