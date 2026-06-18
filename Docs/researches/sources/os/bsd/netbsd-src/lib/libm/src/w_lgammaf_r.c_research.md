# File Research: sources/os/bsd/netbsd-src/lib/libm/src/w_lgammaf_r.c

Wrapper for reentrant float `lgammaf_r(x, signgamp)`. It delegates to `__ieee754_lgammaf_r()` and reports pole or overflow in legacy modes.

Important dependencies: `math.h`, `math_private.h`, `floorf()`, `finitef()`, and `__kernel_standard`.

Legacy error codes match `lgammaf()`: `115` for poles and `114` for overflow.
