# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/arm/sys/sbrk.S

This ARM `sbrk` implementation defines hidden `__curbrk` initialized to `_end`. It reads the current break, adds the requested increment, invokes the `break` syscall, updates `__curbrk` on success, and returns the old break value.
