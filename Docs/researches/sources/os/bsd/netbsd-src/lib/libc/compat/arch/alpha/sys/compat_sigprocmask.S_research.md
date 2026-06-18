# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/arch/alpha/sys/compat_sigprocmask.S

## Scope

Alpha compatibility implementation of old `sigprocmask`.

## Behavior

- Performs architecture-specific argument adaptation for old integer signal masks.
- Calls `compat_13_sigprocmask13` and stores the old mask when requested.

## Dependencies And Invariants

- Pointer-versus-value mask conversion must match old libc ABI.
