# File Research: sources/os/bsd/netbsd-src/lib/libc/softfloat/nexf2.c

Read completely: 31 lines.

Defines `__nexf2` for extended double-precision not-equal comparison when `FLOATX80` is enabled. Normal builds return `!floatx80_eq(a, b)`; `X80M68K` maps the m68k comparison result to `1` or `0`.

Risk: architecture-specific comparison truth convention must remain synchronized with the `floatx80_eq` implementation.
