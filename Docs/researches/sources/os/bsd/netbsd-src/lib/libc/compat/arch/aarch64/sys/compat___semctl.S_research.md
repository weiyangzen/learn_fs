# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/arch/aarch64/sys/compat___semctl.S

## Scope

AArch64 compatibility wrapper for `__semctl`.

## Behavior

- Defines `PSEUDO(__semctl,compat_14___semctl)`.

## Dependencies And Invariants

- Routes the public libc symbol to the NetBSD 1.4-compatible semaphore control syscall.
