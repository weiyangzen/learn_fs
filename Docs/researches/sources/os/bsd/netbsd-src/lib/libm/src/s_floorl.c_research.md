# File Research: sources/os/bsd/netbsd-src/lib/libm/src/s_floorl.c

Implements `floorl()` for real long double by manipulating extended significand words.

Key behavior: handles implicit/explicit integer-bit layouts, returns `-1.0L` for negative fractional magnitudes below 1, increments negative nonintegral significands before masking, and raises inexact via `huge + x`.

Important dependencies: `namespace.h`, `<machine/ieee.h>`, `EXT_FRACHBITS`, `LDBL_MANT_DIG`, and `INC_MANH`.

Notable risks: carry handling and masks depend on exact long-double representation.
