# File Research: sources/os/bsd/netbsd-src/lib/libm/src/k_cosdf.c

This file implements `__kernel_cosdf(double x)`, a double-evaluated kernel returning float cosine for reduced float arguments.

It uses a short polynomial with double coefficients and returns a float. It is optimized for fast single-precision trig paths that reduce arguments into double precision but need a float result. Optional `INLINE_KERNEL_COSDF` controls whether the function is emitted as static inline.

Dependencies are `math.h`, `math_private.h`, and the local polynomial coefficients.
