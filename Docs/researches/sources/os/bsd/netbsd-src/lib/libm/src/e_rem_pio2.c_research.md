# File Research: sources/os/bsd/netbsd-src/lib/libm/src/e_rem_pio2.c

This file implements double argument reduction `__ieee754_rem_pio2(double x, double *y)` for trigonometric functions.

It returns the integer multiple `n` and stores the remainder `x - n*pi/2` as `y[0] + y[1]`. Small inputs need no reduction, inputs near one `pi/2` use split constants directly, medium inputs use multiplication by `2/pi` and up to three correction rounds, and large inputs are decomposed into base-`2**24` chunks passed to `__kernel_rem_pio2`.

Special Inf/NaN inputs produce NaN remainders. Dependencies include `__kernel_rem_pio2`, `fabs`, and double word extraction.
