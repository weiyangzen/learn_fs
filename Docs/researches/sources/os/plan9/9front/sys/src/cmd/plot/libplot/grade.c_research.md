# File Research: sources/os/plan9/9front/sys/src/cmd/plot/libplot/grade.c

This primitive sets curve approximation grade.

Key behavior:
- Assigns the provided value to `e1->grade`.
- Used by curve routines such as `parabola()` to control subdivision step size.

Filesystem relevance:
- None.
