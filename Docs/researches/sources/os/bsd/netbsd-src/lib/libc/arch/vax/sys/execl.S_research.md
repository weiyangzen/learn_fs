# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/vax/sys/execl.S

## Summary
Implements VAX `_execl()` with weak `execl` alias.

## Key Details
- Builds an `argv` vector pointer from the caller's variadic arguments.
- Pushes path and argv pointer.
- Calls `execv`.
- Returns only if `execv` fails.

## Notes
This is an assembly variadic wrapper around the common `execv` implementation.
