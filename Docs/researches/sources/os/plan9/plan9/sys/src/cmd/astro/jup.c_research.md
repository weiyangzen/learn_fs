# File Research: sources/os/plan9/plan9/sys/src/cmd/astro/jup.c

Computes Jupiter ephemeris.

Key points:
- Sets mean orbital elements from `capt` and `eday`.
- Solves Kepler’s equation.
- Reduces orbital coordinates to the ecliptic.
- Applies fixed longitude/latitude offsets, semidiameter, and magnitude.
- Calls `helio` and `geo`.

Dependencies:
- Uses shared orbital globals and convergence threshold.

Notable behavior:
- Perturbation variables are present but set to zero.
