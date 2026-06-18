# File Research: sources/os/bsd/netbsd-src/lib/libm/src/w_sqrtl.c

Wrapper for long-double `sqrtl(x)` when `__HAVE_LONG_DOUBLE` is defined. It delegates to `__ieee754_sqrtl()` and maps negative input to long-double legacy error code `226` outside IEEE mode.

Important dependencies: `namespace.h`, `math.h`, `math_private.h`, and `isnan()`.

The file is inactive on platforms without long-double support.
