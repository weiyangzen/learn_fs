# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/m68k/hardfloat/floatsidf.S

This helper implements `__floatsidf`, converting a signed int to double with `fmovel` and returning the double through `%d0/%d1` for non-SVR4 ABI.
