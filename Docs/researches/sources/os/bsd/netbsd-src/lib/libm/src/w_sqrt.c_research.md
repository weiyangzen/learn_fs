# File Research: sources/os/bsd/netbsd-src/lib/libm/src/w_sqrt.c

Wrapper for double `sqrt(x)`. It delegates to `__ieee754_sqrt()` and reports negative finite input through `__kernel_standard(x, x, 26)` outside IEEE mode.

Important dependencies: `namespace.h`, `math.h`, `math_private.h`, and `isnan()`.

Also aliases `sqrtl` to double `sqrt` when no long-double implementation exists.
