# File Research: sources/os/bsd/netbsd-src/lib/libm/src/w_logf.c

Wrapper for float `logf(x)`. It delegates to `__ieee754_logf()` and maps zero/negative arguments to float legacy errors outside IEEE mode.

Important dependencies: `namespace.h`, `math.h`, `math_private.h`, and `isnanf()`.

Legacy error codes: `116` for `logf(0)` and `117` for negative arguments.
