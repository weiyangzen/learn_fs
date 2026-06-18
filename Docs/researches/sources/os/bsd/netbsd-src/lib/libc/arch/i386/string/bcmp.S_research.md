# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/i386/string/bcmp.S

This i386 `bcmp` compares memory first by 32-bit words with `repe cmpsl`, then by remaining bytes with `repe cmpsb`. It returns zero for equality and one for any mismatch.
