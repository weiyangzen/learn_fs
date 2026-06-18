# File Research: sources/os/bsd/netbsd-src/lib/libm/src/s_rint.c

Implements double `rint()` according to current rounding mode using the `2^52` addition trick.

Key behavior: returns integral inputs unchanged, handles small magnitudes with signed-zero fixup, returns `x+x` for Inf/NaN, and raises inexact when rounding nonintegral values.

Important dependencies: `math_private.h`, `EXTRACT_WORDS`, `SET_HIGH_WORD`, and `INSERT_WORDS`.

Notable risks: depends on current rounding mode and IEEE double precision.
