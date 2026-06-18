# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/sparc64/sys/getcontext.S

## Summary
Implements SPARC64 `_getcontext()` with weak `getcontext` alias.

## Key Details
- Saves the ucontext pointer.
- Calls `SYS_getcontext`.
- Clears saved `%o0`.
- Stores return PC and next PC into 64-bit mcontext slots.

## Notes
Uses 64-bit register slots and SPARC return-address conventions.
