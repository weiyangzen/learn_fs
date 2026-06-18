# File Research: sources/os/bsd/netbsd-src/lib/libm/src/e_powf.c

This file implements the float version, `__ieee754_powf(float x, float y)`.

It mirrors the double algorithm with float-specific split constants, bit masks, exponent limits, and overflow/underflow thresholds. It determines whether a negative base has an odd or even integer exponent, handles special `y` values and special `x` values up front, computes a split `y*log2(|x|)`, and reconstructs `2**z`.

Dependencies include `fabsf`, `scalbnf`, `__ieee754_sqrtf`, and float word access macros.
