# File Research: sources/os/bsd/netbsd-src/lib/libm/src/s_copysign.c

Implements double `copysign(x, y)` by copying the sign bit from `y` into the high word of `x`.

Key behavior: preserves the magnitude and payload bits of `x`, changing only the sign. Provides long-double aliases when long double is not distinct.

Important dependencies: `math_private.h`, `GET_HIGH_WORD`, and `SET_HIGH_WORD`.

Notable risks: assumes IEEE double sign bit location.
