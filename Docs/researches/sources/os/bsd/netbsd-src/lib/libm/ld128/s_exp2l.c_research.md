# File Research: sources/os/bsd/netbsd-src/lib/libm/ld128/s_exp2l.c

This file implements `exp2l(long double x)` for ld128.

The algorithm uses Gal/Bachelis-style accurate tables. It reduces `x` into an integer scale `k`, a table index `i0`, and a small residual `z - eps[i0]`. It looks up `2^(i/128 + eps[i])`, evaluates a degree-10 polynomial for the residual, and scales by `2**k`.

Exceptional paths handle NaN, infinities, overflow for `x >= 16384`, underflow for `x <= -16495`, and tiny `|x|` returning `1 + x`.

The file uses ld128-specific bit tricks with `union ieee_ext_u`, table bits from the low word after adding a large `redux` constant, and separate scaling for subnormal results.
