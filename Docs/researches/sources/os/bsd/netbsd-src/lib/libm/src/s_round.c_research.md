# File Research: sources/os/bsd/netbsd-src/lib/libm/src/s_round.c

Implements double `round()`, rounding halfway cases away from zero using `floor()`.

Key behavior: returns Inf/NaN unchanged; for positive values floors and increments at `>= 0.5`; for negative values rounds magnitude then restores sign.

Important dependencies: `<math.h>`, `fpclassify`, and `floor`.

Notable risks: simpler than bit-twiddling routines and inherits `floor()` behavior and exceptions.
