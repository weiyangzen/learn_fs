# File Research: sources/os/bsd/netbsd-src/lib/libm/src/k_sincos.h

This header merges double sine and cosine kernels into inline `__kernel_sincos(double x, double y, int iy, double *sn, double *cs)`.

It shares the reduced argument, computes sine through the `k_sin` polynomial and cosine through the `k_cos` polynomial, and writes both results. This avoids duplicated range-reduction and can evaluate shared powers once.

Dependencies are the local sine/cosine coefficient tables and ordinary double arithmetic.
