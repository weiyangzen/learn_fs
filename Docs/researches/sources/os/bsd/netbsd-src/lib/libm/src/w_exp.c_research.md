# File Research: sources/os/bsd/netbsd-src/lib/libm/src/w_exp.c

Wrapper for double `exp()`. It delegates to `__ieee754_exp(x)` and, outside IEEE mode, classifies finite inputs above `o_threshold` as overflow and below `u_threshold` as underflow via `__kernel_standard()` error codes `6` and `7`.

Important dependencies: `namespace.h`, `math.h`, `math_private.h`, `finite()`, and `__ieee754_exp`.

Thresholds are encoded as double constants matching fdlibm limits.
