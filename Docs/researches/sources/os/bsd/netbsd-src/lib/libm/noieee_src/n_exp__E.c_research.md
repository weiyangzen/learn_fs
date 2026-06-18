# File Research: sources/os/bsd/netbsd-src/lib/libm/noieee_src/n_exp__E.c

Implements internal kernel `__exp__E(x, c)`, returning `exp(x+c) - 1 - x` for small `x` where `c` is a correction term.

Key behavior:
- Uses rational approximations to sinh/cosh-derived expressions.
- For `|x| > 1e-19`, evaluates polynomial terms `P`, `Q`, and correction `W`.
- For tiny nonzero `x`, attempts to raise inexact and returns signed zero.
- Has different `Q` polynomial degree on VAX/Tahoe versus IEEE.

Important dependencies: `mathimpl.h` and `copysign()`.

Notable risks:
- Assumes `c << x` and `fl(x+c) == x`; callers must satisfy this contract.
