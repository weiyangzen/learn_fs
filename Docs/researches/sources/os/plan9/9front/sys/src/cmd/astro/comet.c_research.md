# File Research: sources/os/plan9/9front/sys/src/cmd/astro/comet.c

Computes the position for a hard-coded comet element set, currently C/2002 C1 Ikeya-Zhang, with older comet elements retained as commented alternatives.

Important behavior:
- Loads perihelion time, distance, eccentricity, inclination, argument of perihelion, and node into global orbital state.
- Caps eccentricity at `.999` because the solver does not handle hyperbolic orbits.
- Solves Kepler’s equation iteratively, derives true anomaly, radius, ecliptic longitude/latitude, magnitude, and motion.
- Finishes through common `helio()` and `geo()` transforms.

This is a special-case object provider in the same style as planet modules.
