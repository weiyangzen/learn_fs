# File Research: sources/os/bsd/netbsd-src/lib/libc/softfloat/gtxf2.c

Read completely: 31 lines.

Defines `__gtxf2` for extended double-precision greater-than comparison when `FLOATX80` is enabled. Normal builds return `floatx80_lt(b, a)`; `X80M68K` converts m68k comparison results to `1` or `-1`.

Risk: the `X80M68K` branch encodes nonstandard return values relative to ordinary boolean SoftFloat comparisons.
