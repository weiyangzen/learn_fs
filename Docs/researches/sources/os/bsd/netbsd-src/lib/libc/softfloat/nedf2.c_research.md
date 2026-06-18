# File Research: sources/os/bsd/netbsd-src/lib/libc/softfloat/nedf2.c

Read completely: 24 lines.

Defines `__nedf2` for double-precision not-equal comparison. It returns `!float64_eq(a, b)`.

Risk: same behavior as `__eqdf2`; distinction is the compiler helper symbol and caller convention.
