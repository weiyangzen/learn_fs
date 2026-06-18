# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/arch/alpha/sys/compat_Ovfork.S

## Scope

Alpha compatibility wrapper for `vfork`.

## Behavior

- Defines `SYSCALL(vfork)` for the compatibility vfork symbol.

## Dependencies And Invariants

- Uses Alpha syscall wrapper macros; unlike newer arches, this file names the syscall directly as `vfork`.
