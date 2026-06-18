# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/arch/powerpc/sys/compat___sigtramp1.S

Implements PowerPC `__sigtramp_sigcontext_1`.

On entry, `r3/r4/r5` contain signal number/code/sigcontext pointer and `lr` contains the handler address. The trampoline allocates a call frame, calls the handler with `blrl`, computes the sigcontext address, calls `compat_16___sigreturn14`, and exits if sigreturn fails.

This is architecture-specific signal ABI compatibility.
