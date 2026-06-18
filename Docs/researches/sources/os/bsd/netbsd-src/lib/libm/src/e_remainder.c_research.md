# File Research: sources/os/bsd/netbsd-src/lib/libm/src/e_remainder.c

This file implements IEEE double `__ieee754_remainder(double x, double p)`.

It returns `x - [x/p]*p`, where the quotient is rounded to nearest with ties to even. It rejects zero divisor, non-finite `x`, and NaN divisor by returning NaN, reduces `x` with `fmod(x, 2p)`, then adjusts around `p/2` to select the nearest-even remainder and restores the original sign of `x`.

Dependencies include `__ieee754_fmod`, `fabs`, and double word manipulation.
