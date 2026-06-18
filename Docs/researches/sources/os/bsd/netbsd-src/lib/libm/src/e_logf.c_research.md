# File Research: sources/os/bsd/netbsd-src/lib/libm/src/e_logf.c

This file implements `__ieee754_logf(float x)`.

It follows the fdlibm double `log` method with float thresholds and constants: normalize to `2^k*(1+f)`, use a small-`f` shortcut or the `s=f/(2+f)` polynomial, and combine with split `ln2_hi`/`ln2_lo`. It handles zero, negative input, subnormals, infinities, and NaNs.

Dependencies are `math_private.h` float word macros and the local float coefficient set.
