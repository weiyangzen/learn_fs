# File Research: sources/os/bsd/netbsd-src/lib/libm/src/s_scalbn.c

Implements double `scalbn()`, `scalbln()`, and aliases for `ldexp()` by exponent manipulation.

Key behavior: normalizes subnormals by multiplying by `2^54`, handles zero, NaN, Inf, overflow, underflow, normal results, and subnormal results.

Important dependencies: `namespace.h`, `math_private.h`, `copysign`, and word macros.

Notable risks: large `n` guards avoid integer overflow in exponent arithmetic; LP64 and non-LP64 aliasing differs.
