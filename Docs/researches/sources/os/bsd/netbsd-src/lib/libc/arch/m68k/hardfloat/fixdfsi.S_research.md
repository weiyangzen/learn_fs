# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/m68k/hardfloat/fixdfsi.S

This helper implements `__fixdfsi`, converting double to signed int by truncating toward zero with `fintrzd` and moving the long result to `%d0`.
