# File Research: sources/os/bsd/netbsd-src/lib/libm/src/k_sincosf.h

This header defines inline `__kernel_sincosdf(double x, float *sn, float *cs)`, computing float sine and cosine from a double reduced argument.

It uses the same optimized polynomial sets as `k_sindf.c` and `k_cosdf.c`, sharing `z = x*x` and related powers. It returns both results through float pointers.

It is intended for optimized float `sincos` paths after argument reduction.
