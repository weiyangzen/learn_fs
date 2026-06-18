# File Research: sources/os/bsd/netbsd-src/lib/libm/src/s_remquof.c

Implements float `remquof()` with the same shift-and-subtract structure as double `remquo()`.

Key behavior: filters exceptional inputs, normalizes subnormals, computes quotient bits, performs nearest-even remainder fixup, restores sign, and writes signed quotient bits.

Important dependencies: `namespace.h`, `math_private.h`, `fabsf`, `GET_FLOAT_WORD`, and `SET_FLOAT_WORD`.

Notable risks: equal-magnitude path sets `*quo = 1` directly; sign handling differs from the double code in that branch.
