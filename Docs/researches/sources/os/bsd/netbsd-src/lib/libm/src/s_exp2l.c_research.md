# File Research: sources/os/bsd/netbsd-src/lib/libm/src/s_exp2l.c

Dispatch wrapper for long-double `exp2l()`. It includes the ld80 or ld128 backend when real long double is available, otherwise returns `exp2(x)`.

Key behavior: weak-aliases `exp2l`; backend chosen by `LDBL_MANT_DIG`.

Important dependencies: `namespace.h`, `<machine/float.h>`, `<machine/ieee.h>`, `../ld80/s_exp2l.c`, and `../ld128/s_exp2l.c`.

Notable risks: numerical behavior and exception handling live in the backend; fallback narrows to double.
