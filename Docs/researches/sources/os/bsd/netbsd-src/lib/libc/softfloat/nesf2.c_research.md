# File Research: sources/os/bsd/netbsd-src/lib/libc/softfloat/nesf2.c

Read completely: 24 lines.

Defines `__nesf2` for single-precision not-equal comparison. It returns `!float32_eq(a, b)`.

Risk: same underlying behavior as `__eqsf2`; exists for the distinct GCC helper symbol.
