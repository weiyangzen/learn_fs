# File Research: sources/os/bsd/netbsd-src/lib/libm/src/s_modff.c

Implements float `modff()` by clearing fractional bits according to exponent.

Key behavior: stores signed zero as integral part for `|x| < 1`, returns signed fractional zero for integral values, and returns `0.0/x` for Inf/NaN fractional part.

Important dependencies: `math_private.h`, `GET_FLOAT_WORD`, and `SET_FLOAT_WORD`.

Notable risks: IEEE float bit layout assumed.
