# File Research: sources/os/bsd/netbsd-src/lib/libm/src/s_copysignf.c

Implements float `copysignf(x, y)` by replacing `x`'s sign bit with `y`'s sign bit.

Key behavior: leaves all non-sign bits of `x` unchanged, including NaN payload bits.

Important dependencies: `math_private.h`, `GET_FLOAT_WORD`, and `SET_FLOAT_WORD`.

Notable risks: assumes IEEE single-precision encoding.
