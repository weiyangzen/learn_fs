# File Research: sources/os/plan9/9front/sys/src/cmd/astro/jup.c

Computes Jupiter’s apparent position.

Important behavior:
- Sets Jupiter mean orbital elements from `eday`/`capt`.
- Solves Kepler’s equation, reduces to ecliptic longitude/latitude, applies fixed empirical corrections, and sets angular semi-diameter and magnitude.
- Calls `helio()` and `geo()` for apparent topocentric output.

Perturbation terms are effectively zeroed except for fixed longitude/latitude adjustments.
