# File Research: sources/os/bsd/netbsd-src/lib/libm/src/s_frexpf.c

Implements float `frexpf()`.

Key behavior: returns zero/Inf/NaN unchanged with exponent 0; scales subnormals by `2^25`; rewrites exponent bits to produce a `[0.5,1)` mantissa.

Important dependencies: `math_private.h`, `GET_FLOAT_WORD`, and `SET_FLOAT_WORD`.

Notable risks: assumes IEEE float layout.
