# File Research: sources/os/plan9/plan9/sys/src/cmd/plot/libplot/circ.c

Draws an unfilled circle.

Key responsibilities:
- Converts center and radius from plot coordinates to screen coordinates.
- Calls Plan 9 draw `ellipse()` with current foreground color.

Notable behavior:
- Negative radius is accepted by taking its absolute value.
- Radius scaling uses `SCR()`, which depends on the x scale only.
