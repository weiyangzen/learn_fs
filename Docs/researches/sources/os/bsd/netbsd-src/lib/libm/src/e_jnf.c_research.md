# File Research: sources/os/bsd/netbsd-src/lib/libm/src/e_jnf.c

This is the float version of `e_jn.c`, implementing `__ieee754_jnf(int n, float x)` and `__ieee754_ynf(int n, float x)`.

`jnf` mirrors the double algorithm with float thresholds: parity normalization for negative orders/arguments, delegation to `j0f`/`j1f`, forward recurrence for `n <= x`, Taylor fallback for tiny `x`, and continued-fraction plus backward recurrence for `n > x`. It scales the backward recurrence when intermediate values become large to avoid spurious overflow.

`ynf` handles NaN, zero, negative, and infinite inputs, then uses forward recurrence from `y0f` and `y1f`, stopping on `-inf`. Dependencies are the float Bessel primitives, `fabsf`, `__ieee754_logf`, and float bit macros.
