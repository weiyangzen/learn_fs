# File Research: sources/os/bsd/netbsd-src/lib/libc/locale/wcstoul.c

Read completely: 47 lines.

This file instantiates `_wcstoul.h` for `wcstoul`, using `unsigned long` and `ULONG_MAX`.

Important interactions: includes `__wctoint.h` and the unsigned conversion template.

Security/reliability notes: inherits unsigned overflow saturation and negative-input wrapping from `_wcstoul.h`.
