# File Research: sources/os/bsd/netbsd-src/lib/libm/src/s_log1p.c

Implements double `log1p(x)` with FDLIBM cancellation-resistant reduction and polynomial approximation.

Key behavior: handles `x < -1`, `x == -1`, Inf, NaN, tiny inputs, and large inputs; computes correction term when `1+x` is rounded; evaluates a polynomial in `s = f/(2+f)`.

Important dependencies: `namespace.h`, `math_private.h`, split `ln2` constants, and high-word manipulation.

Notable risks: exactness relies on split constants and normalization thresholds; this is shared as `log1pl` fallback when no long double exists.
