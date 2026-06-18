# File Research: sources/os/bsd/netbsd-src/lib/libm/src/w_lgamma_r.c

Wrapper for reentrant double `lgamma_r(x, signgamp)`. It delegates to `__ieee754_lgamma_r()` and applies the same pole/overflow legacy error mapping as `lgamma()`.

Important dependencies: `math.h`, `math_private.h`, `floor()`, `finite()`, and `__kernel_standard`.

The sign is returned through the caller-provided pointer instead of global `signgam`.
