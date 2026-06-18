# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/i386/string/swab.S

This i386 `swab` copies 16-bit words from source to destination while rotating each word by 8 bits. It handles an initial 1-to-7-word group and then an unrolled eight-word loop.
