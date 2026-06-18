# File Research: sources/os/bsd/netbsd-src/lib/libm/src/s_cospil.c

Dispatch wrapper for long-double `cospil()`. It includes the ld80 or ld128 implementation when long double is available, otherwise falls back to double `cospi()`.

Key behavior: sets weak alias `cospil/_cospil`; compile-time selects `../ld80/s_cospil.c` or `../ld128/s_cospil.c`.

Important dependencies: `namespace.h`, `<machine/float.h>`, `<machine/ieee.h>`, and backend long-double sources.

Notable risks: behavior is entirely delegated to the selected backend; fallback loses long-double precision.
