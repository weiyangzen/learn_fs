# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/powerpc/sys/__sigtramp2.S

This file implements PowerPC `__sigtramp_siginfo_2` and detailed DWARF CFI for signal-frame unwinding. It describes GPRs, FPR/AltiVec DWARF numbering notes, LR, CTR, CR2, XER, and the signal-return PC using offsets into the saved ucontext.

The runtime trampoline moves the ucontext pointer from `%r30` into `%r3`, calls `setcontext`, and if that fails calls `exit`. It is critical for correct signal return and debugger/unwinder behavior on PowerPC.
