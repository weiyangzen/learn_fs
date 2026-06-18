# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/i386/sys/__sigtramp2.S

This i386 signal trampoline describes the signal frame to DWARF CFI, computes the ucontext pointer from the stack layout, passes it to `setcontext`, and exits with `-1` if `setcontext` returns.
