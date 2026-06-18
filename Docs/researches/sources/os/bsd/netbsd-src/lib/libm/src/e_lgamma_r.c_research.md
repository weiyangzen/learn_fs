# File Research: sources/os/bsd/netbsd-src/lib/libm/src/e_lgamma_r.c

This file implements the reentrant double logarithmic gamma function `__ieee754_lgamma_r(double x, int *signgamp)`.

It uses fdlibm’s domain split: tiny inputs return `-log(|x|)`, negative non-integers use the reflection formula with a local `sin_pi()` reducer, values near 1 and 2 use polynomial/rational approximations, values in `[2,8)` reduce by recurrence, and large values use a Stirling-style expansion. The sign of `Gamma(x)` is stored through `signgamp`.

Special cases include NaN/Inf, zero, negative integers, exact 1 and 2, and very large values. Dependencies include `floor`, `fabs`, `__ieee754_log`, `__kernel_sin`, `__kernel_cos`, and direct double word access.
