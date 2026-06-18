# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/mips/sys/__sigtramp2.S

This file implements the MIPS `__sigtramp_siginfo_2` signal-return trampoline. It emits DWARF CFI for the saved general registers, MDHI/MDLO, and signal-return PC within the signal frame’s ucontext.

At runtime it computes the ucontext address after `siginfo_t`, calls `setcontext`, then calls `exit` with the error code if restoration fails. This file is essential for signal return correctness and stack unwinding across signal handlers.
