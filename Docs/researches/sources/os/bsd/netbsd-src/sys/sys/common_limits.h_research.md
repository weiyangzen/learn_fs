# File Research: sources/os/bsd/netbsd-src/sys/sys/common_limits.h

Defines common scalar limits for `<limits.h>`-style consumers using compiler builtin constants and NetBSD feature-test gates.

Key content:
- Character, short, int, long, and unsigned limits.
- C99/NetBSD long long limits: `LLONG_*`, `ULLONG_MAX`.
- POSIX/XOpen/NetBSD values such as `SSIZE_MAX`, `LONG_BIT`, `WORD_BIT`.
- NetBSD-only aliases: `SSIZE_MIN`, `SIZE_T_MAX`, `UQUAD_MAX`, `QUAD_*`.
- Floating-point limit exposure under XOpen/NetBSD: `DBL_*`, `FLT_*`, optionally `LDBL_*`.

Important behavior:
- Uses `<sys/featuretest.h>` to control namespace exposure.
- Unsigned maxima are computed from signed maxima for core integer types.
