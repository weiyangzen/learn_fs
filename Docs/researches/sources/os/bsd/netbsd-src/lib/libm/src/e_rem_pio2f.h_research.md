# File Research: sources/os/bsd/netbsd-src/lib/libm/src/e_rem_pio2f.h

This header defines `__ieee754_rem_pio2fd(float x, double *y)`, a float-input argument reducer that computes the remainder in double precision.

For medium inputs below about `2**28*pi/2`, it rounds `x * 2/pi` to an integer, subtracts a split `pi/2`, and writes one double remainder. Large inputs are scaled and passed as one chunk to the double `__kernel_rem_pio2`.

It supports optional forced inlining via `INLINE_REM_PIO2F`. Dependencies include `<float.h>`, `rnint`, `irint`, `__kernel_rem_pio2`, and float bit macros.
