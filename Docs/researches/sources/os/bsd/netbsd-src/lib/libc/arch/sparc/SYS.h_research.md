# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/sparc/SYS.h

## Summary
Defines SPARC syscall assembly macros for libc.

## Key Details
- Includes machine assembly, syscall numbers, and trap constants.
- Defines `CERROR` and `CURBRK` symbol naming for ELF and non-ELF.
- Provides PIC-aware `CALL()` and `ERROR()` helpers.
- Defines `_SYSCALL`, `SYSCALL`, `RSYSCALL`, `PSEUDO`, `WSYSCALL`, and no-error variants.
- Uses `ST_SYSCALL`, `%g1` for syscall number, and `SYSCALL_G5RFLAG` for optimized return handling.

## Notes
This file centralizes the SPARC syscall ABI contract used by all SPARC syscall stubs.
