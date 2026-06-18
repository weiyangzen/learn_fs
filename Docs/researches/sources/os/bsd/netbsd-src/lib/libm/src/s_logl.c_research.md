# File Research: sources/os/bsd/netbsd-src/lib/libm/src/s_logl.c

Dispatch wrapper for long-double `logl()`, `log10l()`, `log2l()`, and `log1pl()`.

Key behavior: only builds under `__HAVE_LONG_DOUBLE`; selects ld80 or ld128 backend by `LDBL_MANT_DIG`.

Important dependencies: `namespace.h`, `<machine/float.h>`, `<machine/ieee.h>`, `../ld80/s_logl.c`, and `../ld128/s_logl.c`.

Notable risks: all numerical behavior is in the included backend source.
