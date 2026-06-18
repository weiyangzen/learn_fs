# File Research: sources/os/bsd/netbsd-src/lib/libm/src/w_atanhf.c

Wrapper for float `atanhf()`. It delegates to `__ieee754_atanhf(x)` and maps `|x| > 1` to `__kernel_standard(..., 130)` and `|x| == 1` to `__kernel_standard(..., 131)`.

Important dependencies: `math.h`, `math_private.h`, `fabsf()`, and `isnanf()`.

It exists solely to preserve legacy libm error behavior around the IEEE kernel.
