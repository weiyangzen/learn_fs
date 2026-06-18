# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/arch/arm/sys/compat_sigprocmask.S

## Scope

ARM compatibility implementation of old `sigprocmask`.

## Behavior

- Defines explicit `ENTRY(sigprocmask)`.
- Converts a signal-set pointer argument to the old integer mask value.
- Calls `compat_13_sigprocmask13` and stores the old mask if requested.

## Dependencies And Invariants

- Handles null new-mask pointer by using the old ABI’s equivalent no-change/block-empty behavior.
