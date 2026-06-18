# File Research: sources/os/plan9/9front/sys/src/cmd/astro/merc.c

Computes Mercury’s apparent position.

Important behavior:
- Uses mean orbital elements plus perturbation arguments for Venus, Earth, Jupiter, and Saturn.
- Uses `mercfp`/`merccp` through `cosadd` to compute longitude and radius perturbations.
- Solves Kepler’s equation, reduces to ecliptic coordinates, computes phase magnitude, then calls `helio()`/`geo()`.

This is one of the table-driven inner-planet modules.
