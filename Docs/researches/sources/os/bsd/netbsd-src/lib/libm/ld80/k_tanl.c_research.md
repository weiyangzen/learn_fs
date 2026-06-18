# File Research: sources/os/bsd/netbsd-src/lib/libm/ld80/k_tanl.c

This file implements ld80 `__kernel_tanl(long double x, long double y, int iy)`.

It handles reduced tangent arguments, transforming values near `pi/4` with split constants before evaluating the polynomial. Coefficients are tuned for ld80; on x86 the leading tangent and pi/4 constants are split into volatile double pieces.

The function supports both tangent and reciprocal tangent paths through the historical `iy` interface. The reciprocal path uses compensated arithmetic to compute `-1/(x+r)` more accurately than direct division.

As in ld128, a comment flags that `osign` handling is likely wrong for negative zero.
