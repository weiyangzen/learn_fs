# File Research: sources/os/bsd/netbsd-src/lib/libm/src/s_sinf.c

Implements float `sinf()` using float kernels and argument reduction.

Key behavior: direct kernel path for `|x| <= pi/4`, NaN for Inf/NaN, and quadrant dispatch after `__ieee754_rem_pio2f()`.

Important dependencies: `namespace.h`, `math_private.h`, `__kernel_sinf`, `__kernel_cosf`, and `__ieee754_rem_pio2f`.

Notable risks: threshold and reduction accuracy are float-specific.
