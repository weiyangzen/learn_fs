# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/riscv/sys/__sigtramp2.S

This file implements RISC-V `__sigtramp_siginfo_2` and DWARF signal-frame CFI. It describes all general-purpose registers and a signal-return pseudo-register using offsets into the ucontext located after `siginfo_t` on the stack.

The runtime trampoline computes the ucontext address as `sp + SIGINFO_SIZE`, calls `setcontext` through the no-error syscall path, and calls `exit` if signal return fails. It is critical for signal return and stack unwinding.
