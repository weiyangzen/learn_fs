# File Research: sources/os/bsd/netbsd-src/lib/libc/locale/wcstoumax.c

Read completely: 48 lines.

This file instantiates `_wcstoul.h` for `wcstoumax`, using `uintmax_t` and `UINTMAX_MAX`.

Important interactions: includes `__wctoint.h` and the unsigned conversion template.

Security/reliability notes: inherits unsigned conversion semantics from `_wcstoul.h`.
