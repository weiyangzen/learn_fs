# File Research: sources/os/bsd/netbsd-src/lib/libm/src/w_j1f.c

Wrapper for float Bessel functions `j1f()` and `y1f()`. It mirrors the double wrapper with float kernels and float error codes.

Important dependencies: `math.h`, `math_private.h`, `__ieee754_j1f`, `__ieee754_y1f`, `fabsf()`, `isnanf()`, and `X_TLOSS`.

Legacy error codes: `136`/`137` for TLOSS, `110` for `y1f(0)`, and `111` for `y1f(x < 0)`.
