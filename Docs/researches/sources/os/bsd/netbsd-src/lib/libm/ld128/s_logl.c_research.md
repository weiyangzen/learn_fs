# File Research: sources/os/bsd/netbsd-src/lib/libm/ld128/s_logl.c

This file implements ld128 `logl`, `log1pl`, `log10l`, and `log2l`.

The core algorithm decomposes `x` into `X * 2**k`, chooses one of 128 intervals, and evaluates `log(1+d)` where `d` is very small. Tables `T[]` provide reciprocal-like `G`, high log terms, and long-double low terms. Optional table `U[]` provides exact helper values to compute `d` accurately without a manual split.

`k_logl()` can return a high/low struct when `STRUCT_RETURN` is enabled; `log10l()` and `log2l()` use this split result and multiply by split inverse constants for accuracy. `log1pl()` performs a separate `1+x` decomposition to avoid cancellation for small `x`.

Special cases include zero to `-Inf`, negative to NaN, subnormal scaling by `2^113`, and Inf/NaN passthrough.
