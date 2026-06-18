# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/arch/alpha/sys/compat_msgctl.S

## Scope

Alpha compatibility wrapper for `msgctl`.

## Behavior

- Emits compatibility warning reference.
- Defines `PSEUDO(msgctl,compat_14_msgctl)`.

## Dependencies And Invariants

- Preserves NetBSD 1.4 message-control ABI.
