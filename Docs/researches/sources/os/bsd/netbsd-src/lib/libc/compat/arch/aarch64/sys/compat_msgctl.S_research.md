# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/arch/aarch64/sys/compat_msgctl.S

## Scope

AArch64 compatibility wrapper for `msgctl`.

## Behavior

- Emits a warning reference recommending `<sys/msg.h>`.
- Defines `PSEUDO(msgctl,compat_14_msgctl)`.

## Dependencies And Invariants

- Preserves old SysV message-control ABI.
