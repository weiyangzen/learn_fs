# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/arch/arm/sys/compat_sigpending.S

## Scope

ARM compatibility implementation of old `sigpending`.

## Behavior

- Defines explicit `ENTRY(sigpending)`.
- Calls the compatibility syscall and writes the returned integer mask through the user-provided pointer.

## Dependencies And Invariants

- Must adapt between old integer signal-mask ABI and pointer-based libc function shape.
