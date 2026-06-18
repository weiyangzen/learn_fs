# File Research: sources/os/plan9/plan9/sys/src/cmd/map/libmap/gall.c

Read fully: 29 lines, 512 bytes. SHA-256 prefix: `fb6d1da6dcac2cde`.

Implements a Gall-style projection parameterized by standard latitude. `gall(par)` rejects absolute parameter over 80 degrees, computes an x scale from half-angle cosine, and returns `Xgall`. The projection computes y as `tan(lat/2)` using one of two formulas for numerical stability, and x as scaled negative longitude.

Risk notes: static `scale` supports only one active parameterization.
