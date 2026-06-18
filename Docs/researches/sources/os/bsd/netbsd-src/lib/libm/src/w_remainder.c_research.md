# File Research: sources/os/bsd/netbsd-src/lib/libm/src/w_remainder.c

Wrapper for double `remainder(x, y)`. It delegates to `__ieee754_remainder()` and maps `y == 0` to `__kernel_standard(x, y, 28)` outside IEEE mode, unless `y` is NaN.

Important dependencies: `math.h`, `math_private.h`, `isnan()`, and `__kernel_standard`.

The wrapper does not explicitly test `x` for NaN.
