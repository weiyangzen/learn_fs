# File Research: sources/os/plan9/plan9/sys/src/cmd/plot/libplot/poly.c

Draws one or more open polylines.

Key responsibilities:
- Iterates `num[]` counts and matching point arrays.
- Moves to each polygon/polyline start.
- Draws vectors through each subsequent point.

Notable behavior:
- Stops when it reaches a zero count sentinel.
- Does not close the path unless the input repeats the first point.
