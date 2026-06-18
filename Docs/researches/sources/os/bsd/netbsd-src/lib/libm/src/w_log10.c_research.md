# File Research: sources/os/bsd/netbsd-src/lib/libm/src/w_log10.c

Wrapper for double `log10(x)`. It calls `__ieee754_log10(x)` and maps zero/negative arguments to legacy errors outside IEEE mode.

Important dependencies: `namespace.h`, `math.h`, `math_private.h`, and `isnan()`.

Legacy error codes: `18` for `log10(0)` and `19` for `log10(x < 0)`.
