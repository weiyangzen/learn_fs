# File Research: sources/os/plan9/plan9/sys/src/cmd/astro/helio.c

Converts ecliptic heliocentric coordinates to equatorial geocentric coordinates.

Key points:
- Computes geocentric distance and light-time correction.
- Adds Earth/Sun position vector for annual parallax.
- Applies an approximate annual aberration correction.
- Applies nutation through longitude adjustment and true obliquity.
- Sets `alpha`, `delta`, horizontal parallax, semidiameter scaling, and magnitude distance correction.

Dependencies:
- Uses current Sun/Earth vectors from `setime`.

Notable behavior:
- Comment explicitly notes the stellar aberration method is incorrect.
