# File Research: sources/os/plan9/plan9/sys/src/cmd/map/libmap/rectangular.c

Implements an equirectangular/rectangular projection with configurable standard parallel.

Key functions:
- `rectangular(double par)` stores `scale = cos(par*RAD)`.
- Rejects projections with `scale < .1`, avoiding near-polar standard parallels.
- `Xrectangular()` maps `x = -scale*lon`, `y = lat`.
- Always returns `1`.

This projection is also used as a fallback by conic projections in degenerate cases.
