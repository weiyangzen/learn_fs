# File Research: sources/os/bsd/netbsd-src/lib/libm/src/w_jnf.c

Wrapper for float Bessel functions `jnf(n, x)` and `ynf(n, x)`. It delegates to float IEEE kernels and maps total-loss, zero-pole, and negative-domain cases in non-IEEE modes.

Important dependencies: `math.h`, `math_private.h`, `__ieee754_jnf`, `__ieee754_ynf`, `fabsf()`, `isnanf()`, and `X_TLOSS`.

Legacy error codes: `138`/`139` for TLOSS, `112` for `ynf(n, 0)`, and `113` for `ynf(n, x < 0)`.
