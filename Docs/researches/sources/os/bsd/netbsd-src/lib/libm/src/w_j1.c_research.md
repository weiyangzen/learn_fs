# File Research: sources/os/bsd/netbsd-src/lib/libm/src/w_j1.c

Wrapper for double Bessel functions `j1()` and `y1()`. It delegates to the IEEE kernels and reports total-loss, zero-pole, and negative-domain cases outside IEEE mode.

Important dependencies: `math.h`, `math_private.h`, `__ieee754_j1`, `__ieee754_y1`, `fabs()`, `isnan()`, and `X_TLOSS`.

Legacy error codes: `36`/`37` for TLOSS, `10` for `y1(0)`, and `11` for `y1(x < 0)`.
