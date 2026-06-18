# File Research: sources/os/bsd/netbsd-src/lib/libm/src/e_sqrtf.c

This file implements correctly rounded software float `__ieee754_sqrtf(float x)`.

It is the float analogue of the double bit-by-bit square-root algorithm: handles Inf/NaN, signed zero, and negative inputs; normalizes subnormals; adjusts exponent parity; builds the root bit by bit; and uses `one +/- tiny` to choose final rounding and raise inexact when needed.

Dependencies are `GET_FLOAT_WORD`/`SET_FLOAT_WORD` and basic integer arithmetic.
