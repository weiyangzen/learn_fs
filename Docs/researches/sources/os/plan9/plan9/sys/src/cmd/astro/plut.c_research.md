# File Research: sources/os/plan9/plan9/sys/src/cmd/astro/plut.c

Computes Pluto ephemeris from tabulated orbital elements.

Key points:
- Uses a local element/rate table.
- Solves Kepler’s equation and reduces to ecliptic coordinates.
- Applies fixed longitude/latitude offsets and computes motion/semidiameter.
- Contains a Saturn-ring-style magnitude computation block copied into this Pluto routine.
- Calls `helio` and `geo`.

Dependencies:
- Uses global ephemeris state.

Notable behavior:
- Comments in the magnitude block refer to Saturn even though this file is Pluto.
