# File Research: sources/os/bsd/netbsd-src/lib/libm/src/w_remainderf.c

Wrapper for float `remainderf(x, y)`. It delegates to `__ieee754_remainderf()` and maps zero divisor to float legacy error code `128`.

Important dependencies: `math.h`, `math_private.h`, `isnanf()`, and `__kernel_standard`.

This is the float counterpart to `w_remainder.c`.
