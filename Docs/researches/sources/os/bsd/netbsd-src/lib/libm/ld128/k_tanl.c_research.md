# File Research: sources/os/bsd/netbsd-src/lib/libm/ld128/k_tanl.c

This file implements the ld128 tangent kernel `__kernel_tanl(long double x, long double y, int iy)`.

It evaluates `tan(x+y)` or its reciprocal form for reduced arguments. For inputs near `pi/4`, it transforms the argument using split `pio4`/`pio4lo` constants to maintain accuracy. The polynomial coefficients `T3..T57` approximate `tan(x)/x`.

The `iy` parameter is converted to the historical interface convention: one path returns tangent, the other returns `-1/tan`. The reciprocal path uses a compensated division sequence instead of a simple reciprocal.

The code notes a likely issue around `-0` sign handling in `osign`, which is inherited from the original implementation.
