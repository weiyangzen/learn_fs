# File Research: sources/os/bsd/netbsd-src/lib/libc/softfloat/getf2.c

Read completely: 28 lines.

Defines `__getf2` for quadruple-precision greater-or-equal comparison when `FLOAT128` is enabled. It returns `float128_le(b, a) - 1`.

Risk: compiled only with `FLOAT128`; behavior follows `float128_le`.
