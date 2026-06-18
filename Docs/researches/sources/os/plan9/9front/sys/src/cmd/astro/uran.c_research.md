# File Research: sources/os/plan9/9front/sys/src/cmd/astro/uran.c

Computes Uranus’s apparent position from epoch element coefficients.

Important behavior:
- Interpolates orbital elements, solves Kepler’s equation, and reduces to ecliptic coordinates.
- Applies fixed longitude/latitude corrections.
- Uses the same outer-planet magnitude block as Saturn/Neptune/Pluto style code.
- Calls `helio()` and `geo()`.

The code structure is nearly identical to the Neptune and Pluto modules.
