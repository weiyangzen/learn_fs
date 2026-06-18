# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/arm/sys/__sigtramp2.S

This ARM signal trampoline is used only for returning from a signal; the kernel calls the handler directly. It declares CFI for the signal frame, passes the ucontext pointer from `r5` to `setcontext`, and if that fails invokes `exit` with the error code.
