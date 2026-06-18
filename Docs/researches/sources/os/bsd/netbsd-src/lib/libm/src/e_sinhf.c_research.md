# File Research: sources/os/bsd/netbsd-src/lib/libm/src/e_sinhf.c

This file implements float `__ieee754_sinhf(float x)`.

It is the float analogue of `e_sinh.c`: special Inf/NaN handling, tiny-input return, `expm1f` for `|x| < 22`, `0.5*expf(|x|)` for the normal large range, half-exponent multiplication near overflow, and forced overflow for larger inputs.

Dependencies include `expm1f`, `__ieee754_expf`, `fabsf`, and float word extraction.
