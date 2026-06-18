# File Research: sources/os/bsd/netbsd-src/lib/libc/softfloat/lttf2.c

Read completely: 28 lines.

Defines `__lttf2` for quadruple-precision less-than comparison when `FLOAT128` is enabled. It returns `-float128_lt(a, b)`.

Risk: compiled only with quadruple support.
