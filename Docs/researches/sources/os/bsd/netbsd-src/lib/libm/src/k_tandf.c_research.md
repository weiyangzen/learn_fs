# File Research: sources/os/bsd/netbsd-src/lib/libm/src/k_tandf.c

This file implements `__kernel_tandf(double x, int iy)`, a double-evaluated tangent kernel returning float.

It uses a compact polynomial for float-result tangent and is arranged for parallel evaluation rather than simple Horner form. `iy == 1` returns tangent; otherwise it returns `-1/tan`.

Optional `INLINE_KERNEL_TANDF` controls static-inline emission. Dependencies are local coefficients and ordinary double arithmetic.
