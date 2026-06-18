# File Research: sources/os/plan9/plan9/sys/src/cmd/astro/sat.c

Computes Saturn ephemeris and ring-influenced magnitude.

Key points:
- Builds Saturn orbital elements from epoch, solves Kepler’s equation, and reduces coordinates.
- Applies fixed longitude/latitude offsets and semidiameter.
- Computes geocentric equatorial coordinates and Saturn ring plane geometry to estimate magnitude.
- Calls `helio` and `geo`.

Dependencies:
- Uses shared Sun vector and obliquity globals.

Notable behavior:
- Ring geometry constants are taken from comments citing the Explanatory Supplement.
