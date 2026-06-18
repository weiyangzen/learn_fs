# File Research: sources/os/bsd/netbsd-src/lib/libm/src/s_expl.c

Dispatch wrapper for long-double `expl()` and `expm1l()`. It includes ld80 or ld128 implementations when available, otherwise delegates to double `exp()` and `expm1()`.

Key behavior: defines weak aliases for both functions and selects backend by `LDBL_MANT_DIG`.

Important dependencies: `namespace.h`, `<machine/float.h>`, `<machine/ieee.h>`, `../ld80/s_expl.c`, and `../ld128/s_expl.c`.

Notable risks: fallback loses precision; backend code controls overflow, underflow, and argument reduction details.
