# File Research: sources/os/bsd/netbsd-src/lib/libc/locale/wcstol.c

Read completely: 48 lines.

This file instantiates `_wcstol.h` for `wcstol`, using `long`, `LONG_MIN`, and `LONG_MAX`.

Important interactions: includes `__wctoint.h` and emits both `wcstol` and `wcstol_l` through the template.

Security/reliability notes: inherits signed conversion overflow and invalid-base behavior from the template.
