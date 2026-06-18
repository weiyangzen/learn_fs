# File Research: sources/os/bsd/netbsd-src/lib/libm/ld80/b_expl.c

This file provides the legacy ld80 helper `__exp__LD(long double x, long double c)`.

It computes `exp(x+c)` where `c` is a small correction term, using argument reduction by `k*ln2`, a rational-style correction polynomial, and `ldexpl()` scaling. It is included by the ld80 `b_tgammal.c` implementation, not exposed as a public function.

Constants are stored through `LD80C` unions for exact 80-bit representation. The function handles NaN, overflow, underflow, and infinities explicitly; finite overflow and underflow are forced with large `ldexpl()` calls.

This is legacy BSD gamma support rather than the main modern `expl()` implementation.
