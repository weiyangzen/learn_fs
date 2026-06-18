# File Research: sources/os/plan9/plan9/sys/src/cmd/map/libmap/simpleconic.c

Implements a simple conic projection using one or two standard parallels.

Key behavior:
- `simpleconic(par0, par1)` converts parallels, then chooses parameters:
  - Opposite parallels nearly cancel: fallback to `rectangular(par0)`.
  - Nearly equal parallels: tangent cone formulas.
  - Otherwise: secant cone formulas.
- `Xsimpleconic()` maps by radius `r0 - lat` and angle `a*lon`.
- Always returns `1`.

State:
- Static `r0` and `a` hold projection parameters.
