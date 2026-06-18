# File Research: sources/os/bsd/netbsd-src/lib/libm/src/w_hypotf.c

Wrapper for float `hypotf(x, y)`. It delegates to `__ieee754_hypotf()` and reports overflow if a finite pair produces a nonfinite result outside IEEE mode.

Important dependencies: `namespace.h`, `math.h`, `math_private.h`, `finitef()`, and `__kernel_standard`.

Legacy float overflow error code is `104`.
