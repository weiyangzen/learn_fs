# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/arch/hppa/sys/compat_sigsuspend.S

## Scope

HPPA compatibility implementation of old `sigsuspend`.

## Behavior

- Defines explicit `ENTRY(sigsuspend, 0)`.
- Adapts the caller’s mask pointer to the old integer-mask syscall ABI.

## Dependencies And Invariants

- Signal mask value passing must match `compat_13_sigsuspend13`.
