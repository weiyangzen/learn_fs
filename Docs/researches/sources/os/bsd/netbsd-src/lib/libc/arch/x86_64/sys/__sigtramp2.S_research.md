# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/x86_64/sys/__sigtramp2.S

## Summary
x86_64 siginfo signal trampoline.

## Key Details
- Entry symbol is `__sigtramp_siginfo_2`.
- Provides DWARF CFI for signal-frame unwinding from `ucontext_t` register offsets.
- Uses `%r15` as the ucontext pointer.
- Calls `setcontext` directly by syscall.
- If returning, calls `exit(-1)` by syscall.

## Notes
The file includes a one-byte padding `nop` so unwind lookup at return-PC-minus-one lands inside the trampoline region.
