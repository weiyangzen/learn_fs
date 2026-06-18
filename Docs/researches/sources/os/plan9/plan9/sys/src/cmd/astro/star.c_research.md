# File Research: sources/os/plan9/plan9/sys/src/cmd/astro/star.c

Converts catalog star positions to current apparent coordinates.

Key points:
- Applies E-term aberration removal, proper motion, precession, ecliptic conversion, parallax distance estimate, and then `helio`/`geo`.
- Uses global catalog fields populated by `stars.c`.

Dependencies:
- Uses shared epoch/time globals and observer coordinate conversion pipeline.

Notable behavior:
- Assumes input right ascension is in hours and converts to radians after proper motion.
