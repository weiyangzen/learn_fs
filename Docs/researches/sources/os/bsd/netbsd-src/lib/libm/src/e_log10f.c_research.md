# File Research: sources/os/bsd/netbsd-src/lib/libm/src/e_log10f.c

This is the float implementation of base-10 logarithm, `__ieee754_log10f(float x)`.

It scales subnormal inputs by `2**25`, handles zero, negative, Inf, and NaN, normalizes the significand, and combines `__ieee754_logf(x) * 1/log(10)` with split `log10(2)` exponent terms. The algorithm is the float analogue of `e_log10.c`.

Dependencies include `__ieee754_logf` and float word access macros.
