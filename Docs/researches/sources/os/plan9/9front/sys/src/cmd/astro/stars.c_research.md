# File Research: sources/os/plan9/9front/sys/src/cmd/astro/stars.c

Scans a star catalog for possible Moon occultations.

Important behavior:
- Opens `/lib/sky/estartab`.
- Restricts stars by right ascension near the Moon path.
- Parses SAO id, RA, declination, proper motion, parallax, and magnitude from fixed-width catalog lines.
- Calls `star()` and then `occult(&omoon, &ostar, 0)`.
- Emits occultation begin/end events, with darkness/significance flags based on magnitude.

This module is optional and triggered by the `-o` path in event search.
