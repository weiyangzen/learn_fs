# File Research: sources/os/bsd/netbsd-src/lib/libc/locale/wcstoimax.c

Read completely: 49 lines.

This file instantiates `_wcstol.h` for `wcstoimax`, using `intmax_t`, `INTMAX_MIN`, and `INTMAX_MAX`.

Important interactions: includes `__wctoint.h` and the signed integer conversion template.

Security/reliability notes: inherits base validation and overflow saturation from `_wcstol.h`.
