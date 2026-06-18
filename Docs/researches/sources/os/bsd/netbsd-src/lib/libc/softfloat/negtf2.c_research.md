# File Research: sources/os/bsd/netbsd-src/lib/libc/softfloat/negtf2.c

Read completely: 29 lines.

Defines `__negtf2` for quadruple-precision negation when `FLOAT128` is enabled. It flips the sign bit in `a.high` using the `FLOAT64_MANGLE` sign mask and returns the modified struct.

Risk: assumes the sign bit resides in the high 64-bit word of `float128`.
