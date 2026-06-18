# File Research: sources/os/plan9/plan9/sys/src/cmd/astro/sun.c

Computes solar apparent ecliptic position.

Key points:
- Computes Earth/Sun orbital elements and lunar/planetary arguments.
- Uses `sunfp`/`suncp` coefficient tables for anomaly, longitude, latitude, and radius perturbations.
- Computes longitude, latitude, radius, motion, semidiameter, and magnitude.
- Does not call `helio`/`geo`; caller `fsun` handles that for the apparent Sun pseudo-object.

Dependencies:
- Uses `sunt.c` coefficient data.

Notable behavior:
- `flags['o']` changes the solar semidiameter constant.
