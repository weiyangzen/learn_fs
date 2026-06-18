# File Research: sources/os/bsd/netbsd-src/lib/libm/src/s_sinpil.c

Dispatch wrapper for long-double `sinpil()`. It includes the ld80 or ld128 backend when supported, otherwise falls back to double `sinpi()`.

Key behavior: weak-aliases `sinpil`; selects backend by `LDBL_MANT_DIG`.

Important dependencies: `namespace.h`, `<machine/float.h>`, `<machine/ieee.h>`, `../ld80/s_sinpil.c`, and `../ld128/s_sinpil.c`.

Notable risks: fallback narrows precision; backend code owns exact signed-zero, invalid, and parity behavior.
