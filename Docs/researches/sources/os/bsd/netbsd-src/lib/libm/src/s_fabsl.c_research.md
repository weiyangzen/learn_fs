# File Research: sources/os/bsd/netbsd-src/lib/libm/src/s_fabsl.c

Implements `fabsl()` for real long double by clearing the extended-format sign field.

Key behavior: compiled only under `__HAVE_LONG_DOUBLE`; fallback implementation is intentionally disabled because libc may define it.

Important dependencies: `<machine/ieee.h>` and `union ieee_ext_u`.

Notable risks: depends on `ext_sign` field availability.
