# File Research: sources/os/bsd/netbsd-src/lib/libm/src/w_acos.c

Wrapper for double `acos()`. In IEEE-only builds it returns `__ieee754_acos(x)` directly. Otherwise it calls the kernel first, then routes `|x| > 1` domain errors through `__kernel_standard(x, x, 1)` unless `_LIB_VERSION == _IEEE_` or `x` is NaN.

Important dependencies: `namespace.h`, `math.h`, `math_private.h`, `__ieee754_acos`, `fabs()`, and `__kernel_standard`.

Also provides long-double aliases to double when `__HAVE_LONG_DOUBLE` is absent.
