# File Research: sources/os/bsd/netbsd-src/lib/libm/noieee_src/n_exp.c

Implements legacy `exp()`, `expf()`, and internal `__exp__D()`. It performs `ln2` argument reduction and evaluates a rational correction for `exp(r)`.

Key behavior:
- Handles NaNs, `-Inf`, overflow, and underflow through threshold checks.
- Reduces `x` to `k*ln2 + r`, where `r` is split into high/low pieces.
- Computes `exp(r)` using a polynomial/rational expression involving coefficients `p1` through `p5`.
- Scales the result by `scalb(..., k)`.
- `__exp__D(x,c)` computes `exp(x+c)` for a correction term `c`, used by other legacy functions.
- `expf()` delegates to double `exp()`.

Important dependencies: `../src/namespace.h`, `mathimpl.h`, `finite()`, `copysign()`, and `scalb()`.

Notable risks:
- Overflow/underflow forcing uses very large `scalb()` exponents and relies on legacy floating-point behavior.
