# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/sparc64/sys/cerror.S

## Summary
Implements SPARC64 syscall error handling.

## Key Details
- Reentrant builds call `__errno()` and store the error.
- Non-reentrant builds write global `errno`.
- Supports multiple PIC levels and non-PIC addressing.
- Returns `-1` in both return registers.

## Notes
Entry symbol is `__cerror`, which SPARC64 `SYS.h` targets via `ERROR()`.
