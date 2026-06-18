# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/arch/aarch64/sys/compat_shmctl.S

## Scope

AArch64 compatibility wrapper for `shmctl`.

## Behavior

- Emits a warning reference recommending `<sys/shm.h>`.
- Defines `PSEUDO(shmctl,compat_14_shmctl)`.

## Dependencies And Invariants

- Preserves old SysV shared-memory control ABI.
