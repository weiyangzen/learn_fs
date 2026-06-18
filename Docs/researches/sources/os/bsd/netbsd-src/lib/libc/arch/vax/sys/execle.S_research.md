# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/vax/sys/execle.S

## Summary
Implements VAX `_execle()` with weak `execle` alias.

## Key Details
- Reads the VAX argument count from the call frame.
- Pushes the final argument as `envp`.
- Pushes the variadic argument vector and path.
- Calls `execve`.

## Notes
The implementation depends on VAX call-frame argument-count metadata.
