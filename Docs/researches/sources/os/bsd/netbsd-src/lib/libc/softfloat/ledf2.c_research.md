# File Research: sources/os/bsd/netbsd-src/lib/libc/softfloat/ledf2.c

Read completely: 24 lines.

Defines `__ledf2` for double-precision less-or-equal comparison. It implements libgcc's `1 - (a <= b)` convention via `1 - float64_le(a, b)`.

Risk: adapter only; comparison exceptions are raised by `float64_le`.
