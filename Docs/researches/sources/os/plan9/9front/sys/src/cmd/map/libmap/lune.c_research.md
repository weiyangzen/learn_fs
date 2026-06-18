# File Research: sources/os/plan9/9front/sys/src/cmd/map/libmap/lune.c

Implements a conformal lune projection using the transform `((1+z)^A - (1-z)^A)/((1+z)^A + (1-z)^A)` after stereographic projection.

`lune(lat, theta)` initializes east/west pole reference points, validates expected stereographic symmetry, computes scale and power, then returns `Xlune()`. `Xlune()` rejects points outside the cap, applies stereographic projection, scales, computes complex powers, divides numerator by denominator, and outputs x/y.

It depends on `Xstereographic()`, `cpow()`, and `cdiv()`.
