# File Research: sources/os/bsd/netbsd-src/lib/libc/stdlib/llabs.c

Read completely: 53 lines.

Implements `llabs(long long int)` as `j < 0 ? -j : j`, with a libc weak alias.

It is the long-long variant of the absolute-value wrappers.
