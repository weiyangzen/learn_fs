# File Research: sources/os/bsd/netbsd-src/lib/libm/src/s_tanpil.c

Dispatch wrapper for `tanpil()`. When long double is supported, it includes the format-specific implementation from `../ld80/s_tanpil.c` or `../ld128/s_tanpil.c`; otherwise it falls back to double `tanpi()`.

Important dependencies: `namespace.h`, `math.h`, `<machine/float.h>`, `<machine/ieee.h>`, and `LDBL_MANT_DIG`.

This file contains little independent math logic; its main role is selecting the correct long-double backend and providing the public weak alias.
