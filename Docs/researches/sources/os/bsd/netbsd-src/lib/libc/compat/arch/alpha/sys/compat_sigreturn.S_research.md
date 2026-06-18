# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/arch/alpha/sys/compat_sigreturn.S

## Scope

Alpha compatibility wrapper for old `sigreturn`.

## Behavior

- Defines `PSEUDO(sigreturn,compat_13_sigreturn13)`.

## Dependencies And Invariants

- Preserves the old signal-return syscall ABI.
