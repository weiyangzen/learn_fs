# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/arch/i386/sys/compat___semctl.S

## Scope

i386 compatibility wrapper for `__semctl`.

## Behavior

- Defines `PSEUDO(__semctl,compat_14___semctl)`.

## Dependencies And Invariants

- Routes to old SysV semaphore control syscall.
