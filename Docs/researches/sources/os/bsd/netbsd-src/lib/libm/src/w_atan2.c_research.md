# File Research: sources/os/bsd/netbsd-src/lib/libm/src/w_atan2.c

Wrapper for double `atan2(y, x)`. It delegates to `__ieee754_atan2()` and, in legacy modes, reports the `atan2(+-0, +-0)` case with `__kernel_standard(y, x, 3)`.

Important dependencies: `namespace.h`, `math.h`, `math_private.h`, and `isnan()`.

NaN inputs bypass the wrapper error path.
