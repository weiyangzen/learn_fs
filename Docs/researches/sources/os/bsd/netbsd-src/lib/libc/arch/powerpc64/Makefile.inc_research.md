# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/powerpc64/Makefile.inc

This make include configures PowerPC64 libc architecture sources. It clears `KMINCLUDES` and `KMSRCS`, adds the architecture directory to CPP flags, and adds `__sigtramp2.S`.

It does not include softfloat or miscellaneous cache initialization sources. The file is straightforward build selection for the 64-bit port.
