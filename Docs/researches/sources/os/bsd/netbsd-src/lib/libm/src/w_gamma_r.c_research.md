# File Research: sources/os/bsd/netbsd-src/lib/libm/src/w_gamma_r.c

Implements `gamma_r(x, signgamp)` as a wrapper around `__ieee754_lgamma_r(x, signgamp)`. It preserves legacy error reporting for poles and overflows outside IEEE mode.

Important dependencies: `math.h`, `math_private.h`, `floor()`, `finite()`, and `__kernel_standard`.

Unlike `gamma()`, the sign is written to the caller-provided `signgamp`.
