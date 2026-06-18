# File Research: sources/os/plan9/9front/sys/src/cmd/map/libmap/zcoord.c

This file provides coordinate normalization/orientation helpers for the map library.

Key functions:
- `orient()` sets global map pole, twist, and inverse transform from latitude/longitude/theta.
- `latlon()` normalizes degrees and fills a `place`.
- `deg2rad()` normalizes degrees, fills radians/sine/cosine, and handles exact +/-90 degree cases.
- `sincos()` computes sine/cosine for a `coord`.
- `normalize()` and `invert()` apply global forward/inverse orientation with `norm()`.
- `norm()` rotates a place so a selected pole/twist becomes the map coordinate frame, wrapping longitude to +/-PI.
- `copyplace()` copies a `place`.
- `printp()` debug-prints coordinate internals with stdio.

Most projection files depend on these helpers for pole orientation and safe trigonometric coordinate state.
