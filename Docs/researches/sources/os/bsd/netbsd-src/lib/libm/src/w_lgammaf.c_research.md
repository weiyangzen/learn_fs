# File Research: sources/os/bsd/netbsd-src/lib/libm/src/w_lgammaf.c

Wrapper for float `lgammaf(x)`. It delegates to `__ieee754_lgammaf_r(x, &signgam)` and maps finite-input nonfinite results to pole or overflow errors outside IEEE mode.

Important dependencies: `math.h`, `math_private.h`, `signgam`, `floorf()`, `finitef()`, and `__kernel_standard`.

Legacy error codes: `115` for poles and `114` for overflow.
