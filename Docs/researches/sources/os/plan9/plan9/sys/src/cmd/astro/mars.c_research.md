# File Research: sources/os/plan9/plan9/sys/src/cmd/astro/mars.c

Computes Mars ephemeris.

Key points:
- Builds Mars orbital elements as functions of epoch.
- Solves Kepler’s equation and reduces to ecliptic coordinates.
- Computes motion, apparent semidiameter, and phase-dependent magnitude.
- Calls `helio` and `geo`.

Dependencies:
- Uses global Sun longitude approximation for elongation/magnitude.

Notable behavior:
- Perturbation terms are stubbed as zero.
