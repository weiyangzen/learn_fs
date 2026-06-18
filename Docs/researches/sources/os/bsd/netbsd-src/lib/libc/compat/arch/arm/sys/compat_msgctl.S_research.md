# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/arch/arm/sys/compat_msgctl.S

## Scope

ARM compatibility wrapper for `msgctl`.

## Behavior

- Emits compatibility warning reference.
- Defines `PSEUDO(msgctl,compat_14_msgctl)`.

## Dependencies And Invariants

- Preserves old SysV message-control ABI.
