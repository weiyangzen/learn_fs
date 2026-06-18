# File Research: sources/os/bsd/netbsd-src/lib/libm/src/s_floorf.c

Implements float `floorf()` with direct bit manipulation.

Key behavior: returns `-1.0f` for negative nonzero `|x| < 1`, positive signed zero for positive `|x| < 1`, increments the stored magnitude for negative fractional values before clearing fraction bits, and propagates Inf/NaN as `x+x`.

Important dependencies: `math_private.h`, `GET_FLOAT_WORD`, and `SET_FLOAT_WORD`.

Notable risks: exception behavior depends on the `huge + x` idiom.
