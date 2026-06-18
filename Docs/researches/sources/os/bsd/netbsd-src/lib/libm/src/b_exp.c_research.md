# File Research: sources/os/bsd/netbsd-src/lib/libm/src/b_exp.c

Provides BSD helper `__exp__D(double x, double c)`, computing `exp(x+c)` for split inputs.

Key behavior:
- Handles NaN, underflow, overflow, and infinities.
- Reduces `x` by `k*ln2` using split `ln2hi`/`ln2lo`.
- Uses a degree-5 polynomial correction for `exp(r)`.
- Scales the final result with `scalb`.
- Intended for callers that maintain extra precision in high/low parts, such as old `pow` and gamma code.
