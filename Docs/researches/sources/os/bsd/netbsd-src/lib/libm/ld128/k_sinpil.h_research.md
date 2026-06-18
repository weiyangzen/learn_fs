# File Research: sources/os/bsd/netbsd-src/lib/libm/ld128/k_sinpil.h

This header defines inline `__kernel_sinpil(long double x)` for small reduced `sin(pi*x)` inputs.

It splits `x`, multiplies by split pi constants, normalizes the high/low product with `_2sumF`, and calls `__kernel_sinl(hi, lo, 1)`. Like `k_cospil.h`, it assumes `pi_hi`, `pi_lo`, `_2sumF`, and the kernel sine function are provided by the includer.

Its role is accurate pi multiplication after the public wrapper has already handled quadrants, integers, infinities, and NaNs.
