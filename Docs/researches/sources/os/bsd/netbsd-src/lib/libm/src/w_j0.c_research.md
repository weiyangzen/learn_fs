# File Research: sources/os/bsd/netbsd-src/lib/libm/src/w_j0.c

Wrapper for double Bessel functions `j0()` and `y0()`. `j0()` reports total-loss-of-significance for `|x| > X_TLOSS`; `y0()` reports zero pole, negative domain, and total-loss cases.

Important dependencies: `math.h`, `math_private.h`, `__ieee754_j0`, `__ieee754_y0`, `fabs()`, `isnan()`, and `X_TLOSS`.

Legacy error codes: `34`/`35` for TLOSS, `8` for `y0(0)`, and `9` for `y0(x < 0)`.
