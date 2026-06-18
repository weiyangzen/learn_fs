# File Research: sources/os/bsd/netbsd-src/lib/libm/src/k_cosf.c

This file implements the float cosine kernel `__kernel_cosf(float x, float y)` for reduced arguments.

It mirrors the double `k_cos.c` structure with float coefficients: tiny inputs return 1, a polynomial approximates cosine, `y` corrects for the low tail of argument reduction, and a `qx` split improves accuracy for larger reduced arguments.

Dependencies are float word macros and local coefficient constants.
