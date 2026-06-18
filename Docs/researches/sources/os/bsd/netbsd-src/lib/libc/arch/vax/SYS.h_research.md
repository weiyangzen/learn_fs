# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/vax/SYS.h

## Summary
Defines VAX syscall wrapper macros.

## Key Details
- Uses `chmk` through `SYSTRAP(x)`.
- Defines `CERROR` as `__cerror` and `CURBRK` as `__curbrk`.
- Provides syscall, pseudo-call, raw syscall, weak syscall, and no-error macro variants.
- Tests the carry condition to detect syscall failure.
- Emits a local error branch that jumps into `CERROR+2`.

## Notes
The `CERROR+2` convention is part of the VAX error trampoline layout.
