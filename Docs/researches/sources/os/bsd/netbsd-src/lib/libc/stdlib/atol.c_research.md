# File Research: sources/os/bsd/netbsd-src/lib/libc/stdlib/atol.c

Read completely: 50 lines.

Implements `atol()` as `strtol(str, NULL, 10)`, with a non-null diagnostic assertion.

It is a simple compatibility wrapper over the fuller conversion routine.
