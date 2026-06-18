# File Research: sources/os/bsd/netbsd-src/lib/libm/src/e_sinhl.c

This file implements long-double `sinhl(long double x)` when long double is supported, with a fallback to double `sinh`.

For supported ld80 and ld128 formats, it includes the corresponding long-double exponential kernel, uses polynomial approximations for `|x| < 1`, uses `k_hexpl()` for `1 <= |x| < 64`, uses `hexpl()` up to the overflow threshold, and otherwise overflows with a huge value. Coefficient sets differ for 64-bit and 113-bit mantissas.

It weak-aliases `sinhl` to `_sinhl` and uses `ENTERI`/`RETURNI` precision-control macros, long-double exponent extraction, and `fabsl`.
