# File Research: sources/os/bsd/netbsd-src/lib/libc/locale/wcstoll.c

Read completely: 48 lines.

This file instantiates `_wcstol.h` for `wcstoll`, using `long long int`, `LLONG_MIN`, and `LLONG_MAX`.

Important interactions: includes `__wctoint.h` and the signed conversion template.

Security/reliability notes: inherits overflow checks and ASCII digit mapping from `_wcstol.h`.
