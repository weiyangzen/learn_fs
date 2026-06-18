# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/arch/alpha/sys/compat_sigsuspend.S

## Scope

Alpha compatibility implementation of old `sigsuspend`.

## Behavior

- Performs architecture-specific mask indirection for old signal-set ABI.
- Calls `compat_13_sigsuspend13`.

## Dependencies And Invariants

- Must pass the old integer mask value in the form expected by the compatibility syscall.
