# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/m68k/hardfloat/lesf2.S

This helper implements `__lesf2` and strongly aliases `__gtsf2` to it. It performs a single-precision comparison and returns zero for greater-than, one otherwise.
