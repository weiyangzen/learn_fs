# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/arch/arm/sys/compat_sigreturn.S

## Scope

ARM compatibility wrapper for old `sigreturn`.

## Behavior

- Defines `PSEUDO(sigreturn,compat_13_sigreturn13)`.

## Dependencies And Invariants

- Signal return must preserve restored user context semantics.
