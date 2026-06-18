# File Research: sources/os/plan9/plan9/sys/src/cmd/astro/merc.c

Computes Mercury ephemeris with perturbation series.

Key points:
- Sets Mercury orbital elements and perturbing planet mean anomalies.
- Solves Kepler’s equation.
- Uses `mercfp`/`merccp` through `cosadd` for longitude and radius perturbations.
- Computes ecliptic position, motion, semidiameter, and phase magnitude.
- Calls `helio` and `geo`.

Dependencies:
- Uses coefficient table in `merct.c`.

Notable behavior:
- Latitude perturbation is not applied beyond inclination reduction.
