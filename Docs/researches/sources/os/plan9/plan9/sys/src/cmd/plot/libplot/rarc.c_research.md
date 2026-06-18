# File Research: sources/os/plan9/plan9/sys/src/cmd/plot/libplot/rarc.c

Approximates circular arcs with line segments.

Key responsibilities:
- Computes radius from start point to center.
- Chooses angular step from `e1->quantum`, capped at roughly pi/4.
- Draws clockwise or counterclockwise depending on sign of `rr`.
- Emits line segments by iterative rotation.

Important behavior:
- If radius is tiny relative to `quantum`, draws a degenerate point at the center.
- If arc angle is smaller than one step, draws a straight line.

Notable risks:
- Uses fixed approximations `PI4` and `6.2832`.
- Does not validate that the supplied end point lies on the radius.
