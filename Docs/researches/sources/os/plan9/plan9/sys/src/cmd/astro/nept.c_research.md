# File Research: sources/os/plan9/plan9/sys/src/cmd/astro/nept.c

Computes Neptune ephemeris from tabulated orbital elements.

Key points:
- Uses a local `elem[]` array for epoch, orbital elements, and century rates.
- Solves Kepler’s equation, reduces to ecliptic coordinates, applies fixed offsets, and computes motion/semidiameter.
- Contains a Saturn-ring-style magnitude computation block copied into this outer-planet routine.
- Calls `helio` and `geo`.

Dependencies:
- Uses shared ephemeris globals.

Notable behavior:
- Comments in the magnitude block refer to Saturn even though this file is Neptune.
