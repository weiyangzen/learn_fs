# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/arch/alpha/sys/compat_quotactl.S

## Scope

Alpha compatibility wrapper for `quotactl`.

## Behavior

- Emits compatibility warning reference.
- Defines `PSEUDO(quotactl,compat_50_quotactl)`.

## Dependencies And Invariants

- Routes to NetBSD 5.0 quota compatibility syscall.
