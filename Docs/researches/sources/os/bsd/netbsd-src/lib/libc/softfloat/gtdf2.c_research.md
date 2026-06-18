# File Research: sources/os/bsd/netbsd-src/lib/libc/softfloat/gtdf2.c

Read completely: 24 lines.

Defines `__gtdf2` for double-precision greater-than comparison. It returns `float64_lt(b, a)`.

Risk: thin wrapper; unordered handling is delegated to SoftFloat comparison.
