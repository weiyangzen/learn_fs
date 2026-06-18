# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/vax/sys/__sigtramp3.S

## Summary
Defines the VAX siginfo signal trampoline.

## Key Details
- Entry symbol is `__sigtramp_siginfo_3`.
- Uses the VAX `CALLG` argument-list convention to call the signal handler.
- Adjusts `%ap` to point at the `ucontext_t` argument.
- Calls `setcontext` to return from the signal.
- Contains disabled CFI annotations documenting register offsets.

## Notes
The file documents that VAX DWARF register numbers match `_REG_*` constants.
