# File Research: sources/os/bsd/netbsd-src/lib/libc/softfloat/letf2.c

Read completely: 28 lines.

Defines `__letf2` for quadruple-precision less-or-equal comparison when `FLOAT128` is enabled. It returns `1 - float128_le(a, b)`.

Risk: compiled only with `FLOAT128`.
