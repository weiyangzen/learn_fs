# File Research: sources/os/plan9/plan9/sys/src/cmd/plot/libplot/range.c

Sets user-coordinate range for the active plot environment.

Key responsibilities:
- Sets `xmin` and `ymin`.
- Computes `scalex` and `scaley` from current frame size and requested range.
- Recomputes drawing `quantum`.

Notable risks:
- No divide-by-zero guard for `x1 == x0` or `y1 == y0`.
