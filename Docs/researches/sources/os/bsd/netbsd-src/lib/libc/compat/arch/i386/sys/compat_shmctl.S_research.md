# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/arch/i386/sys/compat_shmctl.S

## Scope

i386 compatibility wrapper for `shmctl`.

## Behavior

- Emits compatibility warning reference.
- Defines `PSEUDO(shmctl,compat_14_shmctl)`.

## Dependencies And Invariants

- Preserves old SysV shared-memory control ABI.
