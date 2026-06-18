# File Research: sources/os/plan9/plan9/sys/src/cmd/plot/libplot/mplot.h

Internal header for the Plan 9 draw-backed plot library.

Key responsibilities:
- Includes Plan 9, libc, stdio, draw, and event headers.
- Defines coordinate scaling macros `SCX`, `SCY`, and `SCR`.
- Declares the `penvir` plotting environment and global pointers `e0`, `e1`, `esave`.
- Declares clipping/map rectangles and backend helper prototypes.
- Includes public libplot prototypes from `../plot.h`.

Important state:
- `penvir` stores plot bounds, scale, current position, curve quantum, grade, pen mode/slant/gap, and foreground/background colors.
- `clip*` bounds control line clipping and clear regions.
- `map*` bounds describe the square plotting area inside the screen.

Notable risks:
- Scaling macros assume `e1` is valid and can overflow before the later `BIGINT` checks in some callers.
