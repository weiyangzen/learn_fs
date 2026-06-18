# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/i386/stdlib/llabs.S

This i386 `llabs` implementation handles a 64-bit two-register value on the stack. If the high word is negative, it computes the two's complement across low and high words; it also aliases `imaxabs` to the same implementation.
