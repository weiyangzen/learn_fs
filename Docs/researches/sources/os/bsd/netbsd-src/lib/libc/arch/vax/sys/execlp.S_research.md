# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/vax/sys/execlp.S

## Summary
Implements VAX `_execlp()` with weak `execlp` alias.

## Key Details
- Builds an `argv` vector pointer from variadic arguments.
- Pushes path and argv pointer.
- Calls `execvp`.

## Notes
This is the PATH-searching counterpart to `execl.S`.
