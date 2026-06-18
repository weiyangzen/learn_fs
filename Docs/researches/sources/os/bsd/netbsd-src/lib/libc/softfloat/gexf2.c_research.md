# File Research: sources/os/bsd/netbsd-src/lib/libc/softfloat/gexf2.c

Read completely: 31 lines.

Defines `__gexf2` for extended double-precision greater-or-equal comparison when `FLOATX80` is enabled. Normal builds return `floatx80_le(b, a) - 1`; `X80M68K` builds use the m68k-specific comparison convention and return `-1` or `0`.

Risk: architecture-specific return encoding is easy to break if `floatx80_le` semantics change.
