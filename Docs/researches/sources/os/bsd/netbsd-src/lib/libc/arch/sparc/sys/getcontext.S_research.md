# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/sparc/sys/getcontext.S

## Summary
Implements SPARC `_getcontext()` with weak `getcontext` alias.

## Key Details
- Saves the ucontext pointer before the syscall.
- Calls `SYS_getcontext`.
- Clears the saved `%o0` register in the mcontext.
- Stores return PC and next PC into the saved context.

## Notes
The file writes fixed mcontext offsets for 32-bit SPARC general registers.
