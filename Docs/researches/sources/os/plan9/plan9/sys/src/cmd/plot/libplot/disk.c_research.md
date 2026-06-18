# File Research: sources/os/plan9/plan9/sys/src/cmd/plot/libplot/disk.c

Draws a filled circle.

Key responsibilities:
- Converts center and radius into screen coordinates.
- Calls `fillellipse()` using the current foreground color.

Notable behavior:
- Negative radius is treated as positive.
- Radius uses x-axis scaling through `SCR()`.
