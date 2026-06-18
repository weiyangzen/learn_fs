# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/i386/stdlib/div.S

This i386 `div` implementation uses a hidden structure-return pointer, performs signed division with `idiv`, stores quotient and remainder into the result object, returns the result pointer, and pops the hidden argument with `ret $4`.
