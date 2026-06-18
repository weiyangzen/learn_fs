# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/sh3/sys/__clone.S

## Summary
Implements SH3 `__clone()` and weak `clone` alias.

## Key Details
- Validates that the function pointer and stack pointer are non-null.
- Issues the `SYS___clone` trap with arguments rearranged as `(flags, stack)`.
- In the child, calls the supplied function with `arg`, then calls `_exit()` with its return value.
- Uses `JUMP_CERROR` on syscall failure or invalid input.
- Handles PIC and non-PIC `_exit` dispatch.

## Notes
Correct register preservation matters because the child entry point and argument are carried across the trap boundary.
