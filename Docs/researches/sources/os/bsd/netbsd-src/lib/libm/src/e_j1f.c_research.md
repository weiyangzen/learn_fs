# File Research: sources/os/bsd/netbsd-src/lib/libm/src/e_j1f.c

This file implements the float IEEE Bessel functions `__ieee754_j1f(float)` and `__ieee754_y1f(float)`.

For `j1f`, it handles NaN/Inf, sign symmetry, tiny inputs via `x/2`, small inputs with rational approximation on `[0,2]`, and larger inputs with sine/cosine asymptotic forms. For `y1f`, it handles zero as `-inf`, negative inputs as NaN, tiny positive inputs as `-2/(pi*x)`, small inputs with rational correction involving `j1f(x)*logf(x)`, and large inputs with asymptotic sine/cosine formulas.

The static helpers `ponef()` and `qonef()` choose coefficient tables by magnitude range and evaluate asymptotic correction rational functions for `x >= 2`. Dependencies include `sinf`, `cosf`, `sqrtf`, `fabsf`, `__ieee754_logf`, and float word access macros from `math_private.h`.
