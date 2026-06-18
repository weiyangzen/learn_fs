# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/vax/sys/syscall.S

## Summary
Implements VAX `_syscall()` and weak `syscall` alias.

## Key Details
- Loads the syscall number from the first argument.
- Adjusts the argument list to skip that syscall-number argument.
- Reduces the argument count by one.
- Executes `chmk` with the requested syscall number.
- Jumps to `CERROR+2` on failure.

## Notes
This is the normal raw syscall interface; `__syscall.S` has different argument-list adjustment.
