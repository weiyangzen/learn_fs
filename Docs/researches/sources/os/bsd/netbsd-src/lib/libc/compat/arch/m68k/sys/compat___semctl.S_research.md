# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/arch/m68k/sys/compat___semctl.S

## Scope

m68k compatibility wrapper for `__semctl`.

## Behavior

- Defines `PSEUDO(__semctl,compat_14___semctl)`.

## Dependencies And Invariants

- Routes to the NetBSD 1.4 semaphore compatibility syscall.
