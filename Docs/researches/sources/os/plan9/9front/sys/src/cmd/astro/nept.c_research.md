# File Research: sources/os/plan9/9front/sys/src/cmd/astro/nept.c

Computes Neptune’s apparent position using element table values and a generic outer-planet style routine.

Important behavior:
- Interpolates semi-major axis, eccentricity, inclination, node, perihelion longitude, and mean longitude from epoch coefficients.
- Solves elliptic orbit and reduces to ecliptic coordinates.
- Applies fixed longitude/latitude adjustments and computes magnitude using a Saturn-ring-derived block copied from the outer-planet style code.
- Calls `helio()` and `geo()`.

The magnitude comments still refer to Saturn, indicating shared/copied logic rather than Neptune-specific documentation.
