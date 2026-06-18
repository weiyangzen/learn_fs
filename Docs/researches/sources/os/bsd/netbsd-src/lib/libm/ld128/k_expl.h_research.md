# File Research: sources/os/bsd/netbsd-src/lib/libm/ld128/k_expl.h

This header provides the ld128 exponential kernel used by `expl`, `expm1l`, `cexpl`, and helper scaling paths.

The central routine `__k_expl()` reduces `x` into `k*ln2 + endpoint[n] + r`, using 128 intervals. It then evaluates `exp(r)` with a polynomial and multiplies by a table entry split into high/low parts. The table stores `2^(i/128)` values as long-double high/low pairs.

It also defines `k_hexpl()` and `hexpl()` for half-scaled exponentials and, when complex support is enabled, `__ldexp_cexpl()` for avoiding overflow in complex exponential by splitting the exponent scale.

The ld128 table is larger and more precise than ld80’s; comments note potential performance tradeoffs on architectures where long-double multiplication is slow.
