# File Research: sources/os/bsd/netbsd-src/lib/libc/stdlib/atoi.c

Read completely: 50 lines.

Implements `atoi()` as `(int)strtol(str, NULL, 10)`, with a non-null diagnostic assertion.

Overflow, whitespace, sign, and digit parsing behavior is inherited from `strtol()` and then narrowed to `int`.
