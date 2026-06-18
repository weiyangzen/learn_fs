# File Research: sources/os/bsd/netbsd-src/lib/libm/src/w_lgamma.c

Wrapper for double `lgamma(x)`. It calls `__ieee754_lgamma_r(x, &signgam)` and reports nonpositive integer poles or overflow in non-IEEE modes.

Important dependencies: `math.h`, `math_private.h`, `signgam`, `floor()`, `finite()`, and `__kernel_standard`.

Legacy error codes: `15` for poles and `14` for overflow.
