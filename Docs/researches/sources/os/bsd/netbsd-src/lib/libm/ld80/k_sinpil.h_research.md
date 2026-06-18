# File Research: sources/os/bsd/netbsd-src/lib/libm/ld80/k_sinpil.h

This header defines inline `__kernel_sinpil(long double x)` for ld80 `sin(pi*x)`.

It splits `x` into float high and residual parts, multiplies with split pi constants, normalizes with `_2sumF`, and calls `__kernel_sinl(hi, lo, 1)`.

The helper assumes public-level range and quadrant decisions have already happened. Its only responsibility is accurate pi multiplication and kernel sine evaluation for small fractional inputs.
