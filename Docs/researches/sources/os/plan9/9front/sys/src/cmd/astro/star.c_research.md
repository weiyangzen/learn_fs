# File Research: sources/os/plan9/9front/sys/src/cmd/astro/star.c

Transforms catalog star data to apparent current topocentric coordinates.

Important behavior:
- Removes E-terms of aberration, applies proper motion, and converts RA/declination into rectangular coordinates.
- Applies precession from catalog epoch to current epoch.
- Converts into mean ecliptic system, estimates distance from parallax, then calls `helio()` and `geo()`.

Used by `stars.c` when scanning the star catalog for lunar occultations.
