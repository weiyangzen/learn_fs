# File Research: sources/os/bsd/netbsd-src/lib/libm/src/k_sinpi.h

This header defines inline `__kernel_sinpi(double x)` for small `sin(pi*x)` kernels.

It splits `x`, multiplies by split `pi_hi`/`pi_lo`, normalizes the product with `_2sumF`, and calls `__kernel_sin(hi, lo, 1)`. The including file supplies pi constants and the ordinary sine kernel.

It is helper infrastructure for half-cycle or pi-multiple trigonometric functions.
