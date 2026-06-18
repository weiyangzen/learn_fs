# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/arch/arm/sys/compat_Ovfork.S

## Scope

ARM compatibility wrapper for `vfork`.

## Behavior

- Provides an explicit `ENTRY(vfork)`.
- Performs ARM-specific syscall sequence for old vfork compatibility.

## Dependencies And Invariants

- Must preserve the ABI expectations around parent/child return values from `vfork`.
