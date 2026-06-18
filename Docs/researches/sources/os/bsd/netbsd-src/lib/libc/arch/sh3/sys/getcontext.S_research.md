# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/sh3/sys/getcontext.S

## Summary
Implements SH3 `_getcontext()` with weak `getcontext` alias.

## Key Details
- Uses `_SYSCALL(_getcontext,getcontext)`.
- Saves procedure register `pr` into the ucontext saved PC slot.
- Writes zero into the saved return-value location so restored contexts return zero.

## Notes
The offsets are architecture ABI constants encoded directly in the assembly.
