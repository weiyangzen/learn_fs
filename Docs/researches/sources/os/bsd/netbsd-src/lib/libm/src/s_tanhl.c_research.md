# File Research: sources/os/bsd/netbsd-src/lib/libm/src/s_tanhl.c

Implements `tanhl()` when `__HAVE_LONG_DOUBLE` is available, with separate coefficient sets for 80-bit and 128-bit long double. Very small inputs return signed tiny values with inexact handling; `|x| < 0.25` uses an odd polynomial; larger finite values use `k_hexpl()` and a compensated division helper.

Important dependencies: `namespace.h`, `<float.h>`, `<machine/ieee.h>`, `math_private.h`, `k_expl.h`, `_2sumF`, `GET_LDBL_EXPSIGN`, `ENTERI`, and `RETURNI`.

Special cases: infinities return signed one, NaNs propagate, and `|x| >= 40` returns `1 - tiny` with sign. If long double is unavailable, it falls back to `tanh(x)`.
