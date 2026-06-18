# File Research: sources/os/bsd/netbsd-src/lib/libm/src/w_log10f.c

Wrapper for float `log10f(x)`. It delegates to `__ieee754_log10f()` and maps zero/negative arguments to float legacy error codes.

Important dependencies: `namespace.h`, `math.h`, `math_private.h`, and `isnanf()`.

Legacy error codes: `118` for zero and `119` for negative input.
