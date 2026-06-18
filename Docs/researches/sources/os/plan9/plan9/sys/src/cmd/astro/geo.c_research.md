# File Research: sources/os/plan9/plan9/sys/src/cmd/astro/geo.c

Converts geocentric equatorial coordinates to topocentric equatorial and horizon coordinates.

Key points:
- Uses `alpha`, `delta`, `rp`, `hp`, and observer location globals.
- Computes local hour angle, topocentric declination, adjusted semidiameter, right ascension, azimuth, and elevation.
- Applies diurnal parallax using Earth radius and geocentric latitude.

Dependencies:
- Consumed by all object solvers after heliocentric/geocentric position computation.

Notable behavior:
- Outputs azimuth/elevation in degrees while many internal angles remain radians.
