# File Research: sources/os/bsd/netbsd-src/lib/libm/src/w_cosh.c

Wrapper for double `cosh()`. It calls `__ieee754_cosh(x)` and, outside IEEE mode, maps inputs above the double overflow threshold to `__kernel_standard(x, x, 5)`.

Important dependencies: `namespace.h`, `math.h`, `math_private.h`, `fabs()`, and `isnan()`.

NaNs return the IEEE result; finite overflow is classified by the hard-coded threshold.
