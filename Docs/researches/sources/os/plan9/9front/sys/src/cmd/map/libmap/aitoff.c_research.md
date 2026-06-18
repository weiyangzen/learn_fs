# File Research: sources/os/plan9/9front/sys/src/cmd/map/libmap/aitoff.c

Implements the Aitoff projection. `Xaitoff()` halves longitude, recomputes sine/cosine, normalizes around an equatorial pole, applies azimuthal equal-area projection, then doubles x. `aitoff()` initializes the pole at `(0,0)` and returns the projection function.

It depends on `copyplace()`, `sincos()`, `norm()`, `Xazequalarea()`, and `latlon()`.
