# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/m68k/hardfloat/ltsf2.S

This helper implements `__ltsf2` and strongly aliases `__gesf2` to it. It compares singles and returns `-1` when `a < b`, otherwise zero.
