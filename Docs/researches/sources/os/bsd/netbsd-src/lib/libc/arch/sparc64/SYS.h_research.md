# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/sparc64/SYS.h

## Summary
Defines SPARC64 syscall assembly macros for libc.

## Key Details
- Includes machine assembly, syscall numbers, and trap constants.
- Provides PIC-level-specific `JUMP()` to reach `__cerror`.
- Defines syscall wrapper families: `_SYSCALL`, `SYSCALL`, `RSYSCALL`, `PSEUDO`, `WSYSCALL`, and no-error variants.
- Uses `ST_SYSCALL` and `SYSCALL_G5RFLAG`.
- Declares `__cerror`.

## Notes
This is the macro foundation for SPARC64 syscall wrapper files.
