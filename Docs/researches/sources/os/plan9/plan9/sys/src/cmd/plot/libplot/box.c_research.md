# File Research: sources/os/plan9/plan9/sys/src/cmd/plot/libplot/box.c

Draws an outlined rectangle in plot coordinates.

Key responsibilities:
- Moves to `(x0, y0)`.
- Draws four vector segments through the remaining corners and back to the start.

Dependencies:
- Uses `move()` and `vec()` from libplot.

Notable risks:
- It does not normalize or clip itself; clipping is delegated to `vec()`.
