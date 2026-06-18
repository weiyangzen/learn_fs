# File Research: sources/os/bsd/netbsd-src/lib/libm/src/s_finitef.c

Implements legacy float `finitef()` with branchless exponent-bit testing.

Key behavior: returns 1 for finite floats and 0 for infinities/NaNs.

Important dependencies: `namespace.h`, `math_private.h`, and `GET_FLOAT_WORD`.

Notable risks: IEEE float encoding is assumed.
