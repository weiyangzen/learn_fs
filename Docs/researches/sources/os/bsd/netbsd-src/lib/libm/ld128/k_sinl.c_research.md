# File Research: sources/os/bsd/netbsd-src/lib/libm/ld128/k_sinl.c

This file implements the ld128 sine kernel `__kernel_sinl(long double x, long double y, int iy)`.

It operates on reduced arguments in roughly `[-pi/4, pi/4]`. If `iy == 0`, it evaluates the polynomial for `sin(x)` directly. Otherwise it incorporates `y`, the low part of the reduced argument, to compute `sin(x + y)` accurately.

Coefficients `S1..S12` approximate `sin(x)/x` to ld128 accuracy; the highest terms are stored as double where sufficient.

This kernel is shared by ordinary trig functions, gamma reflection helpers, and `sinpil()`.
