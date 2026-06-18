# File Research: sources/os/plan9/9front/sys/src/cmd/map/libmap/complex.c

This file provides complex arithmetic helpers for projection formulas:
- `cdiv()` defensive complex division.
- `cmul()` multiplication.
- `csq()` square.
- `csqrt()` square root.
- `cpow()` polar-form complex power.

These are used by conformal projections such as Guyou, Lagrange, lune, hex, and tetra.
