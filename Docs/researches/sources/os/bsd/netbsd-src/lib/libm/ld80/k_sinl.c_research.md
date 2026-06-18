# File Research: sources/os/bsd/netbsd-src/lib/libm/ld80/k_sinl.c

This file implements the ld80 sine kernel `__kernel_sinl(long double x, long double y, int iy)`.

It approximates `sin(x+y)` for reduced inputs using a polynomial for `sin(x)/x`. If `iy == 0`, it returns the direct approximation for `sin(x)`; otherwise it incorporates the low argument part `y`.

The first coefficient is split on x86 into volatile double high/low pieces; remaining coefficients are double. The design mirrors the cosine kernel’s emphasis on exact leading terms and efficient double coefficients.
