# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/arch/hppa/sys/compat_sigreturn.S

## Scope

HPPA compatibility implementation of old `sigreturn`.

## Behavior

- Defines explicit `ENTRY(sigreturn, 0)`.
- Invokes compatibility signal-return syscall with HPPA-specific sequence.

## Dependencies And Invariants

- Must preserve user context restoration semantics.
