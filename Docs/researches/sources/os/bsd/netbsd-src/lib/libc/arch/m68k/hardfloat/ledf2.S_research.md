# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/m68k/hardfloat/ledf2.S

This helper implements `__ledf2` and strongly aliases `__gtdf2` to it. It compares doubles and returns zero when `a > b`, otherwise one, matching libgcc comparison helper conventions.
