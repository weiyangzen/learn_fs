# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/arch/arm/sys/compat___semctl.S

## Scope

ARM compatibility wrapper for `__semctl`.

## Behavior

- Defines `PSEUDO(__semctl,compat_14___semctl)`.

## Dependencies And Invariants

- Routes to NetBSD 1.4 semaphore compatibility syscall.
