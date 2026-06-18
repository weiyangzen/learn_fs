# File Research: sources/os/bsd/netbsd-src/lib/libc/softfloat/netf2.c

Read completely: 28 lines.

Defines `__netf2` for quadruple-precision not-equal comparison when `FLOAT128` is enabled. It returns `!float128_eq(a, b)`.

Risk: compiled only with `FLOAT128`.
