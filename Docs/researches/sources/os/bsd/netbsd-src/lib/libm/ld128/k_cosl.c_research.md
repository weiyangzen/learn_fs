# File Research: sources/os/bsd/netbsd-src/lib/libm/ld128/k_cosl.c

This file implements the ld128 cosine kernel `__kernel_cosl(long double x, long double y)` for reduced arguments near zero.

The valid domain is roughly `[-pi/4, pi/4]`. It evaluates a high-degree polynomial in `z = x*x`, using coefficients `C1..C12`, then combines the result as `1 - z/2 + correction - x*y`. The `y` parameter carries the low part of a previously reduced argument.

The comments emphasize that 113-bit precision requires special care around the exact `x^2 / 2` term. The function is used by public trig routines and by pi-multiple trig helpers.

Dependencies are minimal: `math_private.h` and long-double arithmetic.
