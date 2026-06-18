# File Research: sources/os/plan9/plan9/sys/src/cmd/map/libmap/newyorker.c

Implements the New Yorker projection.

Key behavior:
- `newyorker(double a0)` stores angular parameter `a = a0*RAD`.
- `Xnewyorker()` computes polar distance `r = PI/2 - lat`.
- Very small `r` maps to the center.
- Points with `r < a` are rejected.
- Otherwise scale is `log(r/a)`, applied in longitude polar coordinates.

This is a polar projection centered at the north pole with an excluded inner cap controlled by `a`.
