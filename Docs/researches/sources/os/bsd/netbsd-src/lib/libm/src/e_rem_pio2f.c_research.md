# File Research: sources/os/bsd/netbsd-src/lib/libm/src/e_rem_pio2f.c

This file implements float argument reduction `__ieee754_rem_pio2f(float x, float *y)`.

It uses float split constants for small and medium ranges, a 396-hex-digit `2/pi` table for large inputs, and delegates large reductions to `__kernel_rem_pio2f`. It stores the remainder in two float parts and returns the quadrant count with sign.

The medium path includes cancellation checks against a table of `n*pi/2` high words and may perform second or third correction iterations. Dependencies include `fabsf`, float bit macros, and the float kernel reducer.
