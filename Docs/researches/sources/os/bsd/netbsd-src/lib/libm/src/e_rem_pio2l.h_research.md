# File Research: sources/os/bsd/netbsd-src/lib/libm/src/e_rem_pio2l.h

This header provides inline long-double argument reduction `__ieee754_rem_pio2l(long double x, long double *y)` for ld128-style formats.

Medium inputs use 113-bit `2/pi` and split `pi/2` constants, with correction rounds up to 316-bit effective accuracy. Large finite inputs are decomposed into five base-`2**24` chunks and reduced by the shared double `__kernel_rem_pio2`, then recombined into a long-double high/low result.

Inf/NaN produces NaN outputs. The implementation depends on `fpmath.h`, `union IEEEl2bits`, `rnintl`, `i64rint`, and the shared kernel reducer.
