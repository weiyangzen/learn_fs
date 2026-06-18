# File Research: sources/os/bsd/netbsd-src/lib/libm/src/s_cos.c

Implements double `cos()` using kernel cosine/sine functions and `__ieee754_rem_pio2()` argument reduction.

Key behavior: directly calls `__kernel_cos()` for `|x| <= pi/4`, returns NaN for Inf/NaN via `x-x`, and maps quadrants after range reduction.

Important dependencies: `namespace.h`, `math_private.h`, `__kernel_cos`, `__kernel_sin`, and `__ieee754_rem_pio2`.

Notable risks: accuracy depends on shared range-reduction and kernel implementations.
