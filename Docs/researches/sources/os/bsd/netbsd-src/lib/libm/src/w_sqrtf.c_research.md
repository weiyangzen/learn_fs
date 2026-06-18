# File Research: sources/os/bsd/netbsd-src/lib/libm/src/w_sqrtf.c

Wrapper for float `sqrtf(x)`. It delegates to `__ieee754_sqrtf()` and maps negative input to float legacy error code `126` outside IEEE mode.

Important dependencies: `math.h`, `math_private.h`, and `isnanf()`.

NaNs return the IEEE result without wrapper error handling.
