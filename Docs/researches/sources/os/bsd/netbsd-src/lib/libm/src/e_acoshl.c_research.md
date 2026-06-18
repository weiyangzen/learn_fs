# File Research: sources/os/bsd/netbsd-src/lib/libm/src/e_acoshl.c

Implements long-double `acoshl` when long double support is available, otherwise delegates to double `acosh`.

Key behavior:
- Uses long-double exponent/sign inspection.
- Supports 64-bit and 113-bit long-double mantissas.
- Uses `logl`, `sqrtl`, and `log1pl` range formulas matching `acosh`.
- Defines `EXP_LARGE` thresholds by long-double format.
- Returns through `ENTERI`/`RETURNI` macros for floating-point environment handling.
