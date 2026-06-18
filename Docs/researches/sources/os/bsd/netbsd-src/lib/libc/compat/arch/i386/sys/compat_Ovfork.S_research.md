# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/arch/i386/sys/compat_Ovfork.S

## Scope

i386 compatibility implementation of old `vfork`.

## Behavior

- Defines explicit `ENTRY(vfork)`.
- Performs i386-specific syscall entry and parent/child return handling.
- Includes compatibility warning reference behavior.

## Dependencies And Invariants

- Fork-like return register conventions are ABI-sensitive on i386.
