# File Research: sources/os/bsd/netbsd-src/lib/libc/softfloat/gttf2.c

Read completely: 28 lines.

Defines `__gttf2` for quadruple-precision greater-than comparison when `FLOAT128` is enabled. It returns `float128_lt(b, a)`.

Risk: compiled only with quadruple support.
