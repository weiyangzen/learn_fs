# File Research: sources/os/bsd/netbsd-src/lib/libm/src/k_sinf.c

This file implements the float sine kernel `__kernel_sinf(float x, float y, int iy)`.

It mirrors `k_sin.c` with float coefficients and thresholds. It evaluates an odd sine polynomial and either ignores or incorporates the low-order tail `y` depending on `iy`.

Dependencies are float word macros and local float coefficients.
