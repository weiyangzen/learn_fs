# File Research: sources/os/bsd/netbsd-src/lib/libc/stdlib/labs.c

Read completely: 47 lines.

Implements `labs(long)` as `j < 0 ? -j : j`.

The minimum negative `long` case is not separately protected.
