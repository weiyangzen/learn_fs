# File Research: sources/os/bsd/netbsd-src/lib/libc/softfloat/eqtf2.c

Read completely: 26 lines.

Defines `__eqtf2` for quadruple-precision equality when `FLOAT128` is enabled. It returns `!float128_eq(a, b)`.

Risk: compiled only for builds with `FLOAT128`; otherwise contributes no symbol.
