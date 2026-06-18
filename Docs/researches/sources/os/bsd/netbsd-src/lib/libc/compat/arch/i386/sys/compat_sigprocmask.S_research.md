# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/arch/i386/sys/compat_sigprocmask.S

## Scope

i386 compatibility implementation of old `sigprocmask`.

## Behavior

- Defines explicit `ENTRY(sigprocmask)`.
- Converts new-mask pointer into old integer mask argument.
- Calls `compat_13_sigprocmask13`.
- Stores old mask through `oset` when provided.

## Dependencies And Invariants

- Stack argument rewriting must match i386 calling convention.
