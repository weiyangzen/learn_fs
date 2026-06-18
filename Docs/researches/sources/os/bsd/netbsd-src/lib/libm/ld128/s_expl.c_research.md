# File Research: sources/os/bsd/netbsd-src/lib/libm/ld128/s_expl.c

This file implements `expl(long double x)` and `expm1l(long double x)` for ld128.

`expl()` filters NaN/Inf, overflow, underflow, and tiny inputs, then delegates range reduction and table-polynomial evaluation to `__k_expl()` from `k_expl.h`. It scales the returned high/low result by `2**k`, with special handling near max exponent and subnormal scaling.

`expm1l()` has a separate near-zero path using carefully chosen polynomial ranges around `[-0.1659, 0.1659]`, avoiding cancellation in `exp(x)-1`. Outside that range it reuses the same interval/table reduction but recombines terms differently for `k == 0`, `k == -1`, small negative `k`, and large positive `k`.

Floating environment macros `ENTERI`, `RETURNI`, and `RETURNF` preserve expected rounding/exception behavior.
