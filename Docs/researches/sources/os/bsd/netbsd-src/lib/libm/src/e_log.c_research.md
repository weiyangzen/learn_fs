# File Research: sources/os/bsd/netbsd-src/lib/libm/src/e_log.c

This file implements `__ieee754_log(double x)`.

The algorithm normalizes `x = 2^k * (1+f)` with `sqrt(2)/2 < 1+f < sqrt(2)`, computes `log(1+f)` using `s = f/(2+f)` and a degree-14 Remez polynomial, then combines the result with split `ln2_hi`/`ln2_lo` for accurate exponent contribution. It has a small-`f` shortcut using a short series.

Special cases implement IEEE behavior for zero, negative input, subnormals, infinities, and NaNs. Dependencies are only `math.h`, `math_private.h`, and double word manipulation macros.
