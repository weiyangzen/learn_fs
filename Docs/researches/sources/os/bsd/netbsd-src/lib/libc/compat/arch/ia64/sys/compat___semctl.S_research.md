# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/arch/ia64/sys/compat___semctl.S

## Scope

IA64 compatibility wrapper for `__semctl`.

## Behavior

- Defines `PSEUDO(__semctl,compat_14___semctl)`.

## Dependencies And Invariants

- Routes to old SysV semaphore control compatibility syscall.
