# File Research: sources/os/bsd/netbsd-src/lib/libm/src/w_expf.c

Wrapper for float `expf()`. It delegates to `__ieee754_expf(x)` and maps finite overflow/underflow using float thresholds and `__kernel_standard()` codes `106` and `107`.

Important dependencies: `namespace.h`, `math.h`, `math_private.h`, `finitef()`, and `__ieee754_expf`.

NaNs and infinities return the IEEE implementation result.
