# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/vax/sys/__clone.S

## Summary
Implements VAX `__clone()` and weak `clone` alias.

## Key Details
- Validates non-null function and stack arguments.
- Rewrites the argument list for the kernel's expected `(flags, stack)` arguments.
- Calls `SYS___clone` via `chmk`.
- Child calls the function with `arg`, then `_exit()` with the return value.
- Invalid inputs return `EINVAL` through `CERROR`.

## Notes
The file warns that modifying the call argument list does not work for `callg` with a read-only argument list.
