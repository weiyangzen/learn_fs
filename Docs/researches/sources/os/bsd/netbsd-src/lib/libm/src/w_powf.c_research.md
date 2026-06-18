# File Research: sources/os/bsd/netbsd-src/lib/libm/src/w_powf.c

Wrapper for float `powf(x, y)`. It mirrors the double `pow()` wrapper with float kernels and float legacy error codes.

Important dependencies: `math.h`, `math_private.h`, `isnanf()`, `finitef()`, and `__kernel_standard`.

It handles NaN-to-zero, zero-to-zero, zero-to-negative, negative-base non-integer, overflow, and underflow cases.
