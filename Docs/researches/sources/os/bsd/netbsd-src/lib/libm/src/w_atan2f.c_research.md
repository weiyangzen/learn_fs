# File Research: sources/os/bsd/netbsd-src/lib/libm/src/w_atan2f.c

Wrapper for float `atan2f(y, x)`. It delegates to `__ieee754_atan2f()` and maps both-zero arguments to `__kernel_standard(..., 103)` outside IEEE mode.

Important dependencies: `namespace.h`, `math.h`, `math_private.h`, and `isnanf()`.

This is the float analogue of `w_atan2.c`.
