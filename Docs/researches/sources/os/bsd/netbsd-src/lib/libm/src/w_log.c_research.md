# File Research: sources/os/bsd/netbsd-src/lib/libm/src/w_log.c

Wrapper for double `log(x)`. It delegates to `__ieee754_log(x)` and, outside IEEE mode, maps `x == 0` and `x < 0` to legacy errors.

Important dependencies: `namespace.h`, `math.h`, `math_private.h`, `isnan()`, and `__kernel_standard`.

Legacy error codes: `16` for `log(0)` and `17` for negative arguments. Also aliases `logl` to double `log` when long double is unavailable.
