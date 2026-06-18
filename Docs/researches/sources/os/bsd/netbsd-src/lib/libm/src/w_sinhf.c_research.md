# File Research: sources/os/bsd/netbsd-src/lib/libm/src/w_sinhf.c

Wrapper for float `sinhf()`. It delegates to `__ieee754_sinhf()` and maps finite-input overflow to float legacy error code `125`.

Important dependencies: `namespace.h`, `math.h`, `math_private.h`, `finitef()`, and `__kernel_standard`.

All numerical work is performed by the IEEE kernel.
