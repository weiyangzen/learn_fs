# File Research: sources/os/bsd/netbsd-src/lib/libm/src/s_finite.c

Implements legacy double `finite()` with branchless exponent-bit testing.

Key behavior: returns 1 for finite double values and 0 for infinities/NaNs.

Important dependencies: `namespace.h`, `math_private.h`, and `GET_HIGH_WORD`.

Notable risks: IEEE double encoding is assumed.
