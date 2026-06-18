# File Research: sources/os/bsd/netbsd-src/lib/libc/locale/wcstoull.c

Read completely: 47 lines.

This file instantiates `_wcstoul.h` for `wcstoull`, using `unsigned long long int` and `ULLONG_MAX`.

Important interactions: includes `__wctoint.h` and the unsigned conversion template.

Security/reliability notes: inherits base validation and overflow behavior from `_wcstoul.h`.
