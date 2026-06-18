# File Research: sources/os/bsd/netbsd-src/lib/libm/src/w_j0f.c

Wrapper for float Bessel functions `j0f()` and `y0f()`. It mirrors the double wrapper with float kernels and float legacy error codes.

Important dependencies: `math.h`, `math_private.h`, `__ieee754_j0f`, `__ieee754_y0f`, `fabsf()`, `isnanf()`, and `X_TLOSS`.

Legacy error codes: `134`/`135` for TLOSS, `108` for `y0f(0)`, and `109` for `y0f(x < 0)`.
