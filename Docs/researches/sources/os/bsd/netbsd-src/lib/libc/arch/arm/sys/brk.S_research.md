# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/arm/sys/brk.S

This ARM `brk` implementation defines hidden `__minbrk` initialized to `_end`, clamps requested addresses below that minimum, invokes the `break` syscall, stores the accepted address in `__curbrk`, and returns zero on success.
