# File Research: sources/os/bsd/netbsd-src/lib/libm/src/k_cospi.h

This header defines inline `__kernel_cospi(double x)` for small `cos(pi*x)` kernels.

It splits `x` into float high and double low parts, multiplies by split `pi_hi`/`pi_lo`, normalizes the two-part result with `_2sumF`, and calls `__kernel_cos(hi, lo)`. The including file must provide the pi split constants and the ordinary cosine kernel.

This is infrastructure for pi-multiple trigonometric functions after higher-level range reduction.
