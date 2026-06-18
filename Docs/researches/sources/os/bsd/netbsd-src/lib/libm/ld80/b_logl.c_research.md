# File Research: sources/os/bsd/netbsd-src/lib/libm/ld80/b_logl.c

This file provides the ld80 helper `__log__LD(long double x)`, returning a `struct LDouble` high/low decomposition of `log(x)`.

The algorithm mirrors the ld128 `b_logl.c`: normalize with `frexpl`, choose `F = 1 + j/128`, compute a small transformed variable `u`, apply a short polynomial, and add split table values for `log(F)` and `log(2)`.

The result is split with `r.a` rounded to float precision and `r.b` containing the residual. It is used by legacy `tgammal` code to keep extra precision during Stirling-style products.

This file depends on the local `struct LDouble` declaration from its includer and on `math_private.h`.
