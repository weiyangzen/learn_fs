# File Research: sources/os/plan9/plan9/sys/src/cmd/astro/comet.c

Computes a hardcoded comet ephemeris.

Key points:
- Contains several commented comet element sets; active elements are for C/2002 C1 Ikeya-Zhang.
- Solves Kepler’s equation for an eccentric orbit capped at `MAXE = .999`.
- Computes true anomaly, radius, ecliptic longitude/latitude, motion, semi-diameter, and magnitude.
- Calls `helio` and `geo` to produce observable coordinates.

Dependencies:
- Uses shared `astro.h` globals and `etdate`.

Notable behavior:
- Hyperbolic or near-hyperbolic eccentricity is clamped.
