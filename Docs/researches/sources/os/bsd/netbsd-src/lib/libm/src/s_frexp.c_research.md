# File Research: sources/os/bsd/netbsd-src/lib/libm/src/s_frexp.c

Implements double `frexp()`, decomposing `x` into mantissa in `[0.5,1)` and an exponent.

Key behavior: returns zero/Inf/NaN unchanged with exponent 0; scales subnormals by `2^54`; rewrites exponent bits to normalize the mantissa.

Important dependencies: `math_private.h`, `EXTRACT_WORDS`, `GET_HIGH_WORD`, and `SET_HIGH_WORD`.

Notable risks: assumes IEEE double exponent layout.
