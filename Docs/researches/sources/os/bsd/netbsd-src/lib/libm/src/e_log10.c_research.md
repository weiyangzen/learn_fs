# File Research: sources/os/bsd/netbsd-src/lib/libm/src/e_log10.c

This file implements `__ieee754_log10(double x)`.

It handles exceptional inputs like `log`, scales subnormals, extracts an exponent `k`, normalizes the mantissa, and computes `log10(x)` as `k*log10(2)` plus `log(normalized_x)/log(10)`. The base-10 constants are split into high and low pieces so exact powers of 10 in the normal range round as intended under round-to-nearest.

Dependencies include `__ieee754_log`, `math_private.h` word macros, and standard floating-point arithmetic.
