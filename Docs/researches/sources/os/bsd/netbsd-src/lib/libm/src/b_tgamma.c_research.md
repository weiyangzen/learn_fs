# File Research: sources/os/bsd/netbsd-src/lib/libm/src/b_tgamma.c

Implements BSD `tgamma(double)`.

Key behavior:
- For large positive `x`, computes a Stirling-style approximation in split precision and feeds it to `__exp__D`.
- For moderate positive `x`, reduces to a rational approximation near the gamma minimum.
- For small positive `x`, uses argument reduction around zero.
- For negative non-integers, applies the reflection formula using `sin`/`cos`, `large_gam`, and recursive `tgamma`.
- Handles negative integers, zero, infinities, overflow, and underflow.

Important helpers:
- `large_gam`
- `small_gam`
- `smaller_gam`
- `ratfun_gam`
- `neg_gam`
