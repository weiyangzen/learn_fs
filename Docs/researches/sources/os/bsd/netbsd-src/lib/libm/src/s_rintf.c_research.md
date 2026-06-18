# File Research: sources/os/bsd/netbsd-src/lib/libm/src/s_rintf.c

Implements float `rintf()` using the `2^23` addition trick.

Key behavior: handles small values, integral values, Inf/NaN, and current rounding mode; i386 marks the intermediate as volatile to preserve rounding.

Important dependencies: `math_private.h`, `GET_FLOAT_WORD`, and `SET_FLOAT_WORD`.

Notable risks: compiler optimization can break rounding behavior, as noted by the i386 workaround.
