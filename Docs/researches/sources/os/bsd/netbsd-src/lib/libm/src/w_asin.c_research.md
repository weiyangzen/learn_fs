# File Research: sources/os/bsd/netbsd-src/lib/libm/src/w_asin.c

Wrapper for double `asin()`. It calls `__ieee754_asin(x)` and, outside IEEE mode, reports `|x| > 1` through `__kernel_standard(x, x, 2)`.

Important dependencies: `namespace.h`, `math.h`, `math_private.h`, `fabs()`, and `isnan()`.

Also aliases `asinl` to double `asin` when no independent long-double implementation exists.
