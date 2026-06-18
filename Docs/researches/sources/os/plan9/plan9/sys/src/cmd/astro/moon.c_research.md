# File Research: sources/os/plan9/plan9/sys/src/cmd/astro/moon.c

Computes Moon ephemeris using Brown-style lunar perturbation series.

Key points:
- Computes fundamental lunar and solar elements from epoch.
- Applies long-period corrections and scale factors for eccentricity, solar eccentricity, inclination, and parallax.
- Sums longitude, latitude, node, and parallax terms from `moontab[]`, plus explicit planetary terms.
- Converts lunar longitude/latitude/parallax to equatorial coordinates and then topocentric coordinates.
- Sets Moon phase fraction in `mag`, horizontal parallax, and semidiameter.

Dependencies:
- Uses coefficient table in `moont.c`, `sinx`, `cosx`, `geo`, and nutation globals.

Notable behavior:
- `flags['o']` applies an observational latitude adjustment.
