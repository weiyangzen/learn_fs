# File Research: sources/os/bsd/netbsd-src/lib/libm/noieee_src/n_expm1.c

Implements legacy `expm1()` and `expm1f()`. It shares the `ln2` argument reduction model with `exp()` but uses formulas that avoid cancellation near zero.

Key behavior:
- Returns NaNs unchanged on IEEE targets.
- Reduces `x` to `k*ln2 + z + c`.
- For `k == 0`, returns `z + __exp__E(z,c)`.
- For `k == 1`, uses two separate forms depending on `z < -0.25`.
- For larger `k`, handles `1 - 2^-k` carefully based on precision and range.
- Returns `-1` for large negative finite values and overflows for large positive finite values.
- `expm1f()` casts the double result.

Important dependencies: `mathimpl.h`, `__exp__E()`, `scalb()`, `finite()`, and `copysign()`.

Notable risks:
- Several branches are tuned to old `PREC` constants and legacy inexact/overflow behavior.
