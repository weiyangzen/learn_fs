# File Research: sources/os/bsd/netbsd-src/lib/libm/src/w_acoshf.c

Wrapper for float `acoshf()`. It delegates to `__ieee754_acoshf(x)` and maps `x < 1` to `__kernel_standard(..., 129)` outside IEEE mode.

Important dependencies: `math.h`, `math_private.h`, `__ieee754_acoshf`, and `isnanf()`.

All normal computation is in the IEEE implementation; this wrapper supplies legacy error semantics.
