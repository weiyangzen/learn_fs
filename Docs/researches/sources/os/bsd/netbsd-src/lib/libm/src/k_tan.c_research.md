# File Research: sources/os/bsd/netbsd-src/lib/libm/src/k_tan.c

This file implements the double tangent kernel `__kernel_tan(double x, double y, int iy)`.

For reduced arguments, it evaluates an odd tangent polynomial. For inputs near `pi/4`, it transforms to `tan(pi/4-y) = (1-tan(y))/(1+tan(y))`. The `iy` parameter selects either tangent (`1`) or `-1/tan` (`-1`), with the reciprocal path using compensated division to reduce error.

Tiny inputs have special handling, including reciprocal behavior for signed zero. Dependencies include split `pio4` constants, local tangent coefficients, and double word macros.
