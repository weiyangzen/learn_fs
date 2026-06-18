# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/arch/aarch64/sys/compat_Ovfork.S

## Scope

AArch64 compatibility wrapper for old `vfork`.

## Behavior

- Emits a warning reference for compatibility `vfork()`.
- Defines `PSEUDO(vfork,__vfork14)`.

## Dependencies And Invariants

- Relies on `SYS.h` AArch64 syscall wrapper macros.
- Preserves old symbol while routing to `__vfork14`.
