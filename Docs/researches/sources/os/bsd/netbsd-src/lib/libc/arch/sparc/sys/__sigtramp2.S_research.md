# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/sparc/sys/__sigtramp2.S

## Summary
SPARC signal trampoline for siginfo-style signal returns.

## Key Details
- Entry symbol is `__sigtramp_siginfo_2`.
- Computes the `ucontext_t` address from the stack frame, `siginfo_t`, and fixed sizes.
- Calls `setcontext`.
- Calls `exit` if `setcontext` fails.

## Notes
The stack offsets reflect the 32-bit SPARC frame layout.
