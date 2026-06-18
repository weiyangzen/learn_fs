# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/sparc64/sys/__sigtramp2.S

## Summary
SPARC64 siginfo signal trampoline.

## Key Details
- Entry symbol is `__sigtramp_siginfo_2`.
- Uses `BIAS` and `CC64FSZ` to locate `ucontext_t` after the frame and `siginfo_t`.
- Calls `setcontext`.
- Calls `exit` if returning from `setcontext`.

## Notes
The stack offsets are specific to 64-bit SPARC frame layout.
