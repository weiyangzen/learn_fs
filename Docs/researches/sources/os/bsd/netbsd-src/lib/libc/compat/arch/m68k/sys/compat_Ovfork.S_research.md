# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/arch/m68k/sys/compat_Ovfork.S

## Scope

m68k compatibility implementation of old `vfork`.

## Behavior

- Defines explicit `ENTRY(vfork)`.
- Uses m68k-specific syscall/trap sequence for vfork.
- Handles fork-like return conventions for parent and child.

## Dependencies And Invariants

- Return register handling and stack preservation are ABI-sensitive for vfork.
