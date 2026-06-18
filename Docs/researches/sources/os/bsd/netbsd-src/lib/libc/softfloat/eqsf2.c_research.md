# File Research: sources/os/bsd/netbsd-src/lib/libc/softfloat/eqsf2.c

Read completely: 24 lines.

Defines GCC/libgcc helper `__eqsf2` for single-precision equality comparison. It returns `!float32_eq(a, b)`.

Risk: no independent arithmetic logic; it is sensitive only to `float32_eq` NaN/zero semantics and GCC's expected inverted equality result.
