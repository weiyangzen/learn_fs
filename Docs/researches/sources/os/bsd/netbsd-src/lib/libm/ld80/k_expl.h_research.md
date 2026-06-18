# File Research: sources/os/bsd/netbsd-src/lib/libm/ld80/k_expl.h

This header provides the ld80 exponential kernel shared by `expl`, `expm1l`, and `cexpl`.

`__k_expl()` reduces input using 128 intervals and split `ln2/128` constants, then evaluates a polynomial for the residual and combines it with a table of `2^(i/128)` stored as double high/low pairs. It returns high/low pieces plus an exponent scale `k`.

It also defines `k_hexpl()`, `hexpl()`, and complex-only `__ldexp_cexpl()`. The complex helper scales the real exponential in two exponent factors to avoid overflow while multiplying by sine/cosine.

Compared with ld128, this table uses double pairs, and the polynomial is shorter.
