# File Research: sources/os/plan9/9front/sys/src/cmd/astro/plut.c

Computes Pluto’s apparent position from epoch element coefficients.

Important behavior:
- Interpolates orbital elements, solves elliptic orbit, and reduces to ecliptic coordinates.
- Applies fixed longitude/latitude adjustments.
- Reuses outer-planet magnitude code whose comments refer to Saturn.
- Calls `helio()` and `geo()`.

The file’s structure closely matches `nept.c` and `uran.c`.
