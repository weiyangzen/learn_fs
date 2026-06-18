# File Research: sources/os/plan9/9front/sys/src/cmd/astro/moon.c

Computes the Moon’s apparent topocentric position and phase.

Important behavior:
- Builds fundamental lunar/solar elements from `eday` and `capt`.
- Applies long-period corrections, Brown-style scaling factors, and large lunar perturbation series from `moontab`.
- Computes longitude, latitude, horizontal parallax, semi-diameter, and phase proxy.
- Converts to equatorial coordinates with nutation/obliquity and then calls `geo()`.
- `sinx` and `cosx` evaluate lunar coefficient terms with eccentricity/inclination/parallax scaling.

This is the most numerically dense object computation in the group.
