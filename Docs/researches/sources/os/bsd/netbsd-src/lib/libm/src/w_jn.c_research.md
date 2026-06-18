# File Research: sources/os/bsd/netbsd-src/lib/libm/src/w_jn.c

Wrapper for double-order Bessel functions `jn(n, x)` and `yn(n, x)`. The comments describe the kernel recursion strategy; this wrapper delegates computation and supplies legacy error handling for TLOSS, zero poles, and negative `yn` domains.

Important dependencies: `math.h`, `math_private.h`, `__ieee754_jn`, `__ieee754_yn`, `fabs()`, `isnan()`, and `X_TLOSS`.

Legacy error codes: `38`/`39` for TLOSS, `12` for `yn(n, 0)`, and `13` for `yn(n, x < 0)`.
