# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/m68k/hardfloat/ltdf2.S

This helper implements `__ltdf2` and strongly aliases `__gedf2` to it. It compares doubles and returns `-1` when `a < b`, otherwise zero.
