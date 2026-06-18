# File Research: sources/os/bsd/netbsd-src/lib/libm/ld128/e_rem_pio2l.h

This header implements the inline ld128 argument reducer `__ieee754_rem_pio2l(long double x, long double *y)`.

It returns an integer quadrant count and writes the remainder of `x mod pi/2` as `y[0] + y[1]`. Medium-sized inputs use direct multiplication by a 113-bit `2/pi` approximation and up to three correction rounds using split `pi/2` constants. Large inputs are decomposed into base-2^24 chunks and passed to `__kernel_rem_pio2`.

The ld128 constants are wider than the ld80 version: 113 bits of `2/pi` and three 68-bit pieces of `pi/2`. The large-input path builds a five-element `tx` array and a three-element `ty` result.

Special cases set both output words to NaN for Inf/NaN input.
