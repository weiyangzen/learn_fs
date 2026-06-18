# File Research: sources/os/bsd/netbsd-src/lib/libm/src/s_roundf.c

Implements float `roundf()` using `floorf()` and away-from-zero halfway handling.

Key behavior: returns Inf/NaN unchanged; handles positive and negative magnitudes symmetrically.

Important dependencies: `<math.h>`, `fpclassify`, and `floorf`.

Notable risks: inherits `floorf()` edge behavior.
