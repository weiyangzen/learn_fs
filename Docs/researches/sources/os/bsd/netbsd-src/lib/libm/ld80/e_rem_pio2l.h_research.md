# File Research: sources/os/bsd/netbsd-src/lib/libm/ld80/e_rem_pio2l.h

This header implements inline ld80 `__ieee754_rem_pio2l(long double x, long double *y)`.

Medium-sized inputs use a 64-bit `2/pi` approximation and split `pi/2` constants. On x86, some long-double constants are represented as volatile double high/low pairs because long-double constants are slow or problematic on those targets. Large inputs are decomposed into three base-2^24 chunks and passed to `__kernel_rem_pio2`.

It returns the quadrant count and stores the remainder as two long-double words. Inf/NaN produces NaN remainders.

Compared with ld128, this version has smaller medium-size thresholds, fewer chunks, and lower precision constants appropriate to 64-bit extended precision.
