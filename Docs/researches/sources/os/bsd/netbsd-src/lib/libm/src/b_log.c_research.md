# File Research: sources/os/bsd/netbsd-src/lib/libm/src/b_log.c

Provides BSD helper `__log__D(double x)` returning a split natural logarithm.

Key behavior:
- Uses the same 129-entry table-driven algorithm as the no-IEEE `n_log.c` helper.
- Reduces input to `2^m * F * (1+f/F)`.
- Uses split table values and polynomial correction terms.
- Returns `struct Double { a, b }`, where `a` is truncated and `a+b` gives extra precision.
- Handles subnormal exponent adjustment through `logb`/`ldexp`.

This is a kernel helper, not a public `log` implementation.
