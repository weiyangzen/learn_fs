# File Research: sources/os/bsd/netbsd-src/lib/libc/stdlib/abs.c

Read completely: 47 lines.

Implements `abs(int)` as `j < 0 ? -j : j`.

It is the runtime integer absolute-value function. Like the C standard function generally, the minimum negative integer overflow case is not specially handled.
