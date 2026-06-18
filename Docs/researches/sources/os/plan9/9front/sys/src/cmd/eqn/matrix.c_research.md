# File Research: sources/os/plan9/9front/sys/src/cmd/eqn/matrix.c

This file implements matrix column bookkeeping and final matrix assembly.

Key responsibilities:
- `startcol` records the start of a column in the global `lp` array.
- `column` fills in row count and separation for a column.
- `matrix` normalizes row heights and baselines across columns, converts each column into a pile, then concatenates column piles with matrix spacing.

Important implementation notes:
- Matrix layout assumes consistent row counts and a list of columns.
- Row baseline normalization is done before each column is piled.
- Final result uses `Matspace` between column boxes and frees intermediate column pile registers.
