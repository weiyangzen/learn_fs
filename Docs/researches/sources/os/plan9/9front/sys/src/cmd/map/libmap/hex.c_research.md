# File Research: sources/os/plan9/9front/sys/src/cmd/map/libmap/hex.c

Implements a conformal hexagonal world projection. It uses stereographic projection, complex division/square/cube-root/square-root, and elliptic integrals to map hemispheres into a hexagonal layout with reflection for southern regions.

Key functions:
- `hex()` initializes cut longitudes, constants, centers, reflection vectors, and returns `Xhex()`.
- `Xhex()` handles near-cut/equator edge cases, normalizes to a hemisphere, applies complex transforms, calls `elco2()`, and reflects southern sections.
- `hexcut()` supplies custom cut handling along three cut longitudes.

This is one of the more numerically intricate projection files and depends on `reduce()`, `ckcut()`, `norm()`, `Xstereographic()`, and complex helpers.
