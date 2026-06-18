# File Research: sources/os/plan9/9front/sys/src/cmd/astro/helio.c

Converts heliocentric ecliptic object coordinates into geocentric equatorial coordinates.

Important behavior:
- Uses object `lambda`, `beta`, `rad`, `motion`, and the Sun/Earth vector globals.
- Applies light-time correction, annual parallax, approximate aberration, nutation, and obliquity transform.
- Sets `alpha`, `delta`, `rp`, `hp`, and adjusts `semi` and magnitude.

This is the shared bridge from orbital element calculations to apparent sky position.
