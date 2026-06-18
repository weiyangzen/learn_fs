# File Research: sources/os/bsd/netbsd-src/lib/libm/src/s_sin.c

Implements double `sin()` using FDLIBM kernel functions and `pi/2` argument reduction.

Key behavior: calls `__kernel_sin()` for `|x| <= pi/4`, returns NaN for Inf/NaN, and dispatches by quadrant after `__ieee754_rem_pio2()`.

Important dependencies: `namespace.h`, `math_private.h`, `__kernel_sin`, `__kernel_cos`, and `__ieee754_rem_pio2`.

Notable risks: accuracy depends on shared kernel and range-reduction code.
