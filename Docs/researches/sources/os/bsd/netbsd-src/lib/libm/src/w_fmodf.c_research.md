# File Research: sources/os/bsd/netbsd-src/lib/libm/src/w_fmodf.c

Wrapper for float `fmodf(x, y)`. It delegates to `__ieee754_fmodf()` and maps division by zero divisor to `__kernel_standard(..., 127)` outside IEEE mode.

Important dependencies: `math.h`, `math_private.h`, and `isnanf()`.

NaN arguments bypass wrapper error classification.
