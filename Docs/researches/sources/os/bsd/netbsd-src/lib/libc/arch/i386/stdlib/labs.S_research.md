# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/i386/stdlib/labs.S

This i386 `labs` implementation is the long variant of `abs`, loading a 32-bit long, negating if negative, and returning it in `%eax`.
