# File Research: sources/os/plan9/plan9/sys/src/cmd/map/libmap/twocirc.c

Implements two projections whose meridians and parallels are circular arcs.

Key pieces:
- `twocircles()` solves intersection of a meridian circle and a parallel circle, reflecting signs to handle quadrants and using fallback approximations near axes.
- `globular()` returns `Xglobular`, which scales longitude and latitude into the two-circle solver.
- `vandergrinten()` returns `Xvandergrinten`, using a transformed latitude parameter before solving.

Behavior notes:
- `quadratic()` returns `0` on negative discriminant rather than reporting projection failure.
- Both projection functions always return `1`.
