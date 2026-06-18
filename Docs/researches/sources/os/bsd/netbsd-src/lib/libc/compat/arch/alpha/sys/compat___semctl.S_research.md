# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/arch/alpha/sys/compat___semctl.S

## Scope

Alpha compatibility wrapper for `__semctl`.

## Behavior

- Defines `PSEUDO(__semctl,compat_14___semctl)`.

## Dependencies And Invariants

- Routes to the NetBSD 1.4 SysV semaphore compatibility syscall.
