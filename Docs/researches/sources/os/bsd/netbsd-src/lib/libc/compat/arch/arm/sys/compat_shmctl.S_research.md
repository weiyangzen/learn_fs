# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/arch/arm/sys/compat_shmctl.S

## Scope

ARM compatibility wrapper for `shmctl`.

## Behavior

- Emits compatibility warning reference.
- Defines `PSEUDO(shmctl,compat_14_shmctl)`.

## Dependencies And Invariants

- Preserves old SysV shared-memory control ABI.
