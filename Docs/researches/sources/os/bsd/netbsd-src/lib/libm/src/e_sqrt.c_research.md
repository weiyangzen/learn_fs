# File Research: sources/os/bsd/netbsd-src/lib/libm/src/e_sqrt.c

This file implements correctly rounded software double `__ieee754_sqrt(double x)`.

The main implementation is fdlibm’s portable bit-by-bit integer algorithm. It handles NaN/Inf, signed zero, and negative inputs; normalizes subnormal numbers; adjusts odd exponents; generates the square-root significand one bit at a time across high and low words; then uses floating additions with `one +/- tiny` to infer rounding direction and inexact behavior.

The long comment after the implementation documents alternative Newton and reciprocal-root algorithms. Dependencies are double word extraction/insertion macros and no hardware sqrt requirement.
