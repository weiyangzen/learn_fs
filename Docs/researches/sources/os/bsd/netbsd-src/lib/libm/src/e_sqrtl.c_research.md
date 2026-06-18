# File Research: sources/os/bsd/netbsd-src/lib/libm/src/e_sqrtl.c

This file implements long-double `__ieee754_sqrtl(long double x)` when long double exists.

With floating-environment support, it handles NaN/Inf, signed zero, and negative inputs, normalizes subnormals, reduces the exponent, obtains a double `sqrt` estimate, optionally refines for high-precision formats, combines high/low parts, then temporarily switches rounding to toward-zero to perform final correction according to the caller’s rounding mode. Helpers `inc()` and `dec()` move a normal long double by one ulp.

Without fenv support, it falls back to double `__ieee754_sqrt((double)x)`. Dependencies include `<fenv.h>`, `union ieee_ext_u`, machine IEEE layout, and `math_private.h`.
