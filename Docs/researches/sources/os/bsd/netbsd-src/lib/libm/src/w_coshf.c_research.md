# File Research: sources/os/bsd/netbsd-src/lib/libm/src/w_coshf.c

Wrapper for float `coshf()`. It calls `__ieee754_coshf(x)` and maps values above the float overflow threshold to `__kernel_standard(..., 105)` in non-IEEE modes.

Important dependencies: `namespace.h`, `math.h`, `math_private.h`, `fabsf()`, and `isnanf()`.

This wrapper does not implement the hyperbolic algorithm itself.
