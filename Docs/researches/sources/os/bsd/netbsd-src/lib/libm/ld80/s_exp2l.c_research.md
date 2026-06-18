# File Research: sources/os/bsd/netbsd-src/lib/libm/ld80/s_exp2l.c

Implements Intel 80-bit `long double` `exp2l()`. The algorithm is table-driven: reduce `x` into an integer exponent `k`, table index `i`, and small residual `z`, then compute `2^k * exp2(i/TBLSIZE) * polynomial(z)`.

Key behavior:
- Uses a 128-entry table, stored as high/low double pairs, for `exp2(i/128)`.
- Uses a degree-6 minimax polynomial for the small residual.
- Handles `+Inf`, `-Inf`, NaNs, overflow, underflow, and very small inputs before entering the main rounding-sensitive path.
- Builds powers of two by setting ld80 exponent/significand fields directly; uses a `+10000` scaling path for subnormal-range results.

Important dependencies: `math_private.h`, ld80 `union ieee_ext_u`, `GET_EXPSIGN`, `GET_LDBL80_MAN`, `SET_EXPSIGN`, `SET_LDBL80_MAN`, `ENTERI`, and `RETURNI`.

Notable risks:
- The range-reduction bit extraction depends on 80-bit layout and assumes signed right shift for negative exponents, as noted in the source.
- The `redux` trick and direct fraction-word access are format-specific and not portable outside the intended ld80 environment.
