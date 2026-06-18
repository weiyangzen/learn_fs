# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/sparc64/sys/__clone.S

## Summary
Implements SPARC64 `__clone()` and weak `clone` alias.

## Key Details
- Validates function and stack pointers.
- Allocates a 64-bit SPARC caller frame on the child stack, accounting for stack bias.
- Stores function pointer and argument into the child frame.
- Calls `SYS___clone` with `(flags, stack)`.
- Parent returns normally; child calls the function then exits.
- Uses `EINVAL` through `ERROR()` for invalid inputs.

## Notes
The implementation is SPARC64 ABI-specific because of register windows, frame size, and stack bias.
