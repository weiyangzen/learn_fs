# File Research: sources/os/bsd/netbsd-src/lib/libm/src/s_erfl.c

Dispatch wrapper for long-double `erfl()` and `erfcl()`. It includes the ld80 or ld128 implementation when supported, otherwise falls back to double `erf()`/`erfc()`.

Key behavior: defines weak aliases and selects backend by `LDBL_MANT_DIG`.

Important dependencies: `namespace.h`, `<machine/float.h>`, `<machine/ieee.h>`, `../ld80/s_erfl.c`, and `../ld128/s_erfl.c`.

Notable risks: fallback loses precision; backend implementation owns all numerical behavior.
