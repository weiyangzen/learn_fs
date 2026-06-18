# File Research: sources/os/plan9/plan9/sys/src/cmd/astro/uran.c

Computes Uranus ephemeris from tabulated orbital elements.

Key points:
- Uses local element/rate table.
- Solves Kepler’s equation and reduces to ecliptic coordinates.
- Applies fixed offsets and computes motion/semidiameter.
- Contains a Saturn-ring-style magnitude computation block copied into this Uranus routine.
- Calls `helio` and `geo`.

Dependencies:
- Uses shared ephemeris globals.

Notable behavior:
- Comments in the magnitude block refer to Saturn even though this file is Uranus.
