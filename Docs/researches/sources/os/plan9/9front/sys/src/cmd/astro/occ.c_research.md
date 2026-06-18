# File Research: sources/os/plan9/9front/sys/src/cmd/astro/occ.c

Occultation, eclipse, and transit timing helper.

Important behavior:
- `occult` finds local minima in angular separation between two sampled objects.
- Refines candidates first by minute-scale stepping, then by finer interpolation.
- Computes contact times `t1` through `t5` based on apparent semi-diameter sums/differences.
- `set3pt` builds quadratic interpolation coefficients for RA, declination, semi-diameter, and elevation.
- `setpt` evaluates the interpolation; `pinorm` normalizes angle deltas.

Used by `search.c` for Moon occultations, eclipses, and inner-planet transits.
