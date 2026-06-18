# File Research: sources/os/bsd/netbsd-src/lib/libm/src/w_log2.c

Wrapper for double `log2(x)`. It delegates to `__ieee754_log2(x)` and maps zero/negative arguments to log2-specific legacy errors outside IEEE mode.

Important dependencies: `namespace.h`, `math.h`, `math_private.h`, and `isnan()`.

Legacy error codes: `48` for `log2(0)` and `49` for `log2(x < 0)`.
