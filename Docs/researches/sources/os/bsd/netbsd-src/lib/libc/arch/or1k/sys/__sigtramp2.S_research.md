# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/or1k/sys/__sigtramp2.S

This file implements the or1k signal trampoline `__sigtramp_siginfo_2`. It uses the ucontext pointer preserved in `r14`, moves it to the first argument register, calls `setcontext`, and if that fails calls `exit`.

Unlike some other ports in this group, it does not include extensive DWARF CFI metadata. Its runtime role is still critical: returning from signal handlers by restoring the saved machine context.
