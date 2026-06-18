# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/x86_64/SYS.h

## Summary
Defines x86_64 syscall wrapper macros.

## Key Details
- Uses `syscall` instruction with syscall number in `%eax`.
- Moves `%rcx` to `%r10` before syscall to match the kernel ABI.
- Defines `CERROR` as `__cerror` and `CURBRK` as `__curbrk`.
- Provides syscall, pseudo-call, raw syscall, weak syscall, and no-error macro variants.
- Uses carry flag to detect syscall errors and jump to `__cerror`.

## Notes
This header centralizes the x86_64 userspace-to-kernel syscall ABI for libc assembly.
