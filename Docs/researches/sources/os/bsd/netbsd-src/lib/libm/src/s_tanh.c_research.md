# File Research: sources/os/bsd/netbsd-src/lib/libm/src/s_tanh.c

Implements double-precision `tanh()`. It uses fdlibm formulas based on `expm1()` for stable computation across ranges: tiny inputs return approximately `x`, moderate inputs use either `-t/(t+2)` or `1 - 2/(t+2)`, and large finite inputs return `1 - tiny` with sign restoration.

Important dependencies: `math.h`, `math_private.h`, `GET_HIGH_WORD`, `fabs()`, and `expm1()`.

Special cases: infinities return signed one through `one/x +/- one`; NaNs propagate. The `tiny` constant is used to raise inexact for large finite inputs.
