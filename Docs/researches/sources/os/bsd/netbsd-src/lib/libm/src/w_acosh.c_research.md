# File Research: sources/os/bsd/netbsd-src/lib/libm/src/w_acosh.c

Wrapper for double `acosh()`. It delegates to `__ieee754_acosh(x)` and, outside IEEE mode, maps `x < 1` domain errors to `__kernel_standard(x, x, 29)`.

Important dependencies: `math.h`, `math_private.h`, `__ieee754_acosh`, `isnan()`, and `_LIB_VERSION`.

NaNs bypass wrapper errors and return the IEEE result.
