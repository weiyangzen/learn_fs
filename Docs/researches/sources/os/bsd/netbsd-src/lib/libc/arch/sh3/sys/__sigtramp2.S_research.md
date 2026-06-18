# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/sh3/sys/__sigtramp2.S

## Summary
Defines the SH3 signal trampoline used for returning from signal handlers.

## Key Details
- Entry symbol is `__sigtramp_siginfo_2`.
- Expects the stack pointer to address the saved `ucontext_t`.
- Calls `setcontext` using the ucontext pointer.
- If `setcontext` returns, exits with the returned error value.
- Provides DWARF CFI for signal-frame unwinding, mapping SH general and special registers to ucontext offsets.

## Notes
The file documents SH-specific stack ordering where `ucontext_t` is placed before `siginfo`.
