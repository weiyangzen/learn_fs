# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/arch/alpha/sys/compat_shmctl.S

## Scope

Alpha compatibility wrapper for `shmctl`.

## Behavior

- Emits compatibility warning reference.
- Defines `PSEUDO(shmctl,compat_14_shmctl)`.

## Dependencies And Invariants

- Preserves NetBSD 1.4 shared-memory control ABI.
