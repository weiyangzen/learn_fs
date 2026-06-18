# File Research: sources/os/bsd/netbsd-src/lib/libm/ld128/s_cexpl.c

This file implements `cexpl(long double complex z)` for ld128.

It handles special cases first: real-only input, purely imaginary input, non-finite imaginary parts, and infinite real parts. For normal values, it computes `exp(x) * (cos(y) + i*sin(y))`.

When `x` is too large for plain `expl(x)` but still within the complex exponential scaling range, it calls `__ldexp_cexpl()` from `k_expl.h` to avoid intermediate overflow. Constants `exp_ovfl` and `cexp_ovfl` define the direct and scaled thresholds.

This ld128 version uses numeric comparisons rather than ld80-style direct exponent/mantissa inspection.
