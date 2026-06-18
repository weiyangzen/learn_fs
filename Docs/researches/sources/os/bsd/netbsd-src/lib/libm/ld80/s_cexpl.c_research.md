# File Research: sources/os/bsd/netbsd-src/lib/libm/ld80/s_cexpl.c

This file implements ld80 `cexpl(long double complex z)`.

It extracts ld80 words for both real and imaginary components to handle zero, NaN, and infinity cases without relying only on generic predicates. Pure real input returns `expl(x) + I*y`; pure imaginary input returns `cos(y) + I*sin(y)`.

For non-finite imaginary values, it follows complex exponential special-case rules for finite/NaN real, negative infinity real, and positive infinity real. For real parts between direct `expl` overflow and complex overflow, it calls `__ldexp_cexpl()` from `k_expl.h`.

Normal inputs compute `expl(x)` and multiply by `sincosl(y)`.
