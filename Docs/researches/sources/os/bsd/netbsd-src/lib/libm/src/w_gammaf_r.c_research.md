# File Research: sources/os/bsd/netbsd-src/lib/libm/src/w_gammaf_r.c

Implements `gammaf_r(x, signgamp)` as the float reentrant wrapper around `__ieee754_lgammaf_r()`. It reports nonpositive integer poles and overflows using the float legacy error codes.

Important dependencies: `math.h`, `math_private.h`, `floorf()`, `finitef()`, and `__kernel_standard`.

The caller receives the gamma sign through `signgamp`.
