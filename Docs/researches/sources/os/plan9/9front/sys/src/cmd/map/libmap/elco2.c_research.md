# File Research: sources/os/plan9/9front/sys/src/cmd/map/libmap/elco2.c

Implements Bulirsch-style complex elliptic integral routine `elco2()`, used by several conformal polyhedral/square projections. It computes an integral from `0` to `x+iy` with parameters `kc`, `a`, and `b`, returning success/failure and output real/imaginary parts.

Supporting helpers:
- `cdiv2()` computes a stable partial complex division component.
- `csqr()` computes the complex square root of `|x| + iy`.

The routine is numerically specialized and rejects `kc == 0` or negative x.
