# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/x86_64/sys/__clone.S

## Summary
Implements x86_64 `__clone()` and weak `clone` alias.

## Key Details
- Saves `%r12` and `%r13` for function and argument.
- Validates non-null function and stack pointers.
- Rearranges arguments for the kernel's `__clone` syscall.
- Pushes a dummy return address before the syscall.
- Parent restores stack/registers and returns.
- Child calls the supplied function with `arg`, then `_exit()` with the result.
- Invalid inputs return `EINVAL` through the syscall error path.

## Notes
The file uses `PIC_PLT(_exit)` and has a recent revision timestamp.
