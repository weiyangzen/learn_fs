# File Research: sources/os/bsd/netbsd-src/lib/libc/softfloat/gesf2.c

Read completely: 24 lines.

Defines `__gesf2` for single-precision greater-or-equal comparison. It returns `float32_le(b, a) - 1`.

Risk: no independent logic beyond preserving GCC helper return convention.
