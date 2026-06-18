# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/m68k/sys/__sigtramp2.S

This file implements the m68k signal trampoline entry `__sigtramp_siginfo_2`. It includes DWARF CFI metadata describing how general registers and signal return PCs are recoverable from the `ucontext_t` placed on the signal frame.

At runtime the trampoline loads the ucontext pointer from the signal frame, places it into the syscall argument slot, calls `setcontext`, and if that fails calls `exit` with the error code. Correctness is critical for signal return, unwinding through signal frames, debuggers, and exception handling.
