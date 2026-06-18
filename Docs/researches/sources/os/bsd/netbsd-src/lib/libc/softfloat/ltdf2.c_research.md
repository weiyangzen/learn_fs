# File Research: sources/os/bsd/netbsd-src/lib/libc/softfloat/ltdf2.c

Read completely: 24 lines.

Defines `__ltdf2` for double-precision less-than comparison. It returns `-float64_lt(a, b)` per libgcc's `-(a < b)` convention.

Risk: thin return-convention adapter.
