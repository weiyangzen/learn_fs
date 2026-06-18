# File Research: sources/os/plan9/plan9/sys/src/cmd/map/libmap/lambert.c

Implements a Lambert conformal conic projection with two standard parallels.

Key functions:
- `lambert(double par0, double par1)` normalizes parallel order, validates polar limits, and computes cone constant `k`.
- Degenerate cases dispatch to other projections:
  - Near opposite parallels: `mercator()`.
  - Near equal parallels: `perspective(-1.)`, effectively stereographic.
- `Xlambert()` computes radial distance and angular displacement.

Behavior notes:
- Rejects latitudes below about `-80°`.
- Treats near north pole as `r = 0`.
- Negates radius for southern standard-parallel setup.
- Output is `x = -r*sin(k*lon)`, `y = -r*cos(k*lon)`.
