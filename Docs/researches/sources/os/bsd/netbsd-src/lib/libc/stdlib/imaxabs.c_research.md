# File Research: sources/os/bsd/netbsd-src/lib/libc/stdlib/imaxabs.c

Read completely: 49 lines.

Implements `imaxabs(intmax_t)` as `i < 0 ? -i : i`, with a libc weak alias.

It mirrors the other absolute-value functions and does not special-case the minimum representable negative value.
