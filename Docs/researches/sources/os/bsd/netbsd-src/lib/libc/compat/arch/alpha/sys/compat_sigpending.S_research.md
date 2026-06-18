# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/arch/alpha/sys/compat_sigpending.S

## Scope

Alpha compatibility implementation of old `sigpending`.

## Behavior

- Implements architecture-specific handling rather than a simple `PSEUDO` line.
- Calls the compatibility `sigpending13` syscall and stores/returns the old signal mask as required by Alpha ABI.

## Dependencies And Invariants

- Must match Alpha calling convention for pointer arguments and return values.
