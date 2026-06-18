# File Research: sources/os/bsd/netbsd-src/lib/libm/ld80/k_cosl.c

This file implements the ld80 cosine kernel `__kernel_cosl(long double x, long double y)`.

It evaluates `cos(x+y)` for reduced inputs around zero using a polynomial in `x*x`. The leading `x^2/2` term is handled separately for exactness. Coefficients above the first terms are stored as double because that precision is sufficient for ld80.

On x86 targets, the first coefficient is split into volatile double high/low constants to avoid slow or broken long-double constants.

The kernel is used by ordinary trig functions and pi-multiple wrappers.
