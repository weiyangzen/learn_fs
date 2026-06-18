# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/arch/aarch64/sys/compat___sigreturn14.S

## Scope

AArch64 compatibility wrapper for `__sigreturn14`.

## Behavior

- Notes that register state must be preserved.
- Defines `PSEUDO(__sigreturn14,compat_16___sigreturn14)`.

## Dependencies And Invariants

- Signal return wrappers must not disturb user register state before entering the compatibility syscall.
