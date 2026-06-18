# File Research: sources/os/bsd/netbsd-src/lib/libm/src/e_remainderf.c

This file implements float `__ieee754_remainderf(float x, float p)`.

It mirrors the double remainder algorithm: invalid cases return NaN, `x` is reduced with `fmodf(x, p+p)`, exact equality returns signed zero, and comparisons against `p/2` choose the nearest remainder with tie behavior. The original sign bit of `x` is restored at the end.

Dependencies are `__ieee754_fmodf`, `fabsf`, and float word macros.
