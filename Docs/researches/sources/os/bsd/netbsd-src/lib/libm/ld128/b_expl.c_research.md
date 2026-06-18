# File Research: sources/os/bsd/netbsd-src/lib/libm/ld128/b_expl.c

## Scope

Long-double exponential kernel for 80/128-bit style libm support, converted from BSD `b_exp.c`.

## APIs And Behavior

- Defines polynomial coefficients `p1` through `p7` via `LD80C` union constants.
- Defines split `ln2` constants, overflow/underflow thresholds `lnhuge` and `lntiny`, and `invln2`.
- Static `__exp__D(x, c)` computes `exp(x + c)` where `|c| < |x|` and the parts do not overlap.
- Returns NaN unchanged.
- For finite range, reduces `x` by nearest integer `k*ln2`, split into `hi` and `lo`, evaluates a rational correction polynomial, and returns `ldexpl(1 + (hi - (lo - c)), k)`.
- Very negative finite inputs return a forced underflow via `ldexpl(1., -5000)`; very positive finite inputs return forced overflow via `ldexpl(1., 5000)`.
- Infinite inputs return mathematically expected `0`, `Inf`, or `x`.

## Dependencies And Risks

- Depends on `math_private.h`, `union ieee_ext_u`, and `LD80C` constants.
- The function is static in this file as read; inclusion or macro use elsewhere determines its compilation role.
- Threshold constants assume the target long-double exponent range encoded in the file.
