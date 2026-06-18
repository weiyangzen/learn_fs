# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/i386/sys/brk.S

This i386 `brk` defines `__minbrk` initialized to `_end`, clamps requested breaks below that value, invokes the `break` syscall, stores the accepted break in `__curbrk`, and returns zero on success. It has PIC and non-PIC addressing paths.
