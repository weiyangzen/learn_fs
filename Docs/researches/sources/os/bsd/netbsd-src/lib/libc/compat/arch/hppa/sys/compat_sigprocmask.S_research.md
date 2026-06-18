# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/arch/hppa/sys/compat_sigprocmask.S

## Scope

HPPA compatibility implementation of old `sigprocmask`.

## Behavior

- Defines explicit `ENTRY(sigprocmask, 0)`.
- Converts pointer-based mask arguments to old integer mask syscall arguments.
- Stores the previous mask when requested.

## Dependencies And Invariants

- Null mask behavior and old integer mask storage must match historical libc ABI.
