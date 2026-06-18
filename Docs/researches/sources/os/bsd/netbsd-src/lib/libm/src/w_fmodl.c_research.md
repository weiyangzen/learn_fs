# File Research: sources/os/bsd/netbsd-src/lib/libm/src/w_fmodl.c

Wrapper for long-double `fmodl(x, y)` when `__HAVE_LONG_DOUBLE` is defined. It delegates to `__ieee754_fmodl()` and maps `y == 0` to `__kernel_standard(x, y, 227)` outside IEEE mode.

Important dependencies: `namespace.h`, `math.h`, `math_private.h`, `isnan()`, and `__ieee754_fmodl`.

This file compiles no function body when long double support is unavailable.
