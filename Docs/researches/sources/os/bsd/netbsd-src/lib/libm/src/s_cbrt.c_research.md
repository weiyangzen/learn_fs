# File Research: sources/os/bsd/netbsd-src/lib/libm/src/s_cbrt.c

This file implements public double `cbrt(double x)`.

It preserves the sign, handles NaN/Inf and zero directly, forms a rough cube-root estimate from the exponent bits, handles subnormals by scaling, refines with a rational approximation to about 23 bits, rounds the estimate upward after chopping, and performs one Newton step to reach double precision with error below about 0.667 ulp. The sign bit is restored before return.

When long double is absent, it aliases `cbrtl` to `cbrt`. Dependencies include `namespace.h`, `math_private.h`, and double word access macros.
