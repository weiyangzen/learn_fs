# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/hppa/sys/brk.S

This HPPA `brk` implementation defines `__minbrk` as `_end`, clamps requested breaks below that minimum, invokes the `break` syscall, and stores the accepted value in hidden `__curbrk`.
