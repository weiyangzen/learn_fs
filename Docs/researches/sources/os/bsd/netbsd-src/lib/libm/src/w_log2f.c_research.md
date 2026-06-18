# File Research: sources/os/bsd/netbsd-src/lib/libm/src/w_log2f.c

Wrapper for float `log2f(x)`. It delegates to `__ieee754_log2f()` and maps zero/negative arguments to float log2 legacy errors.

Important dependencies: `namespace.h`, `math.h`, `math_private.h`, and `isnanf()`.

Legacy error codes: `148` for zero and `149` for negative input.
