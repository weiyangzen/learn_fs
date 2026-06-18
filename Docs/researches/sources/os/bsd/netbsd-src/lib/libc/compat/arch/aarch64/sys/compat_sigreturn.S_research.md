# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/arch/aarch64/sys/compat_sigreturn.S

## Scope

AArch64 compatibility wrapper for old `sigreturn`.

## Behavior

- Defines compatibility signal-return syscall wrapper for `sigreturn`.
- Routes to `compat_13_sigreturn13`.

## Dependencies And Invariants

- Must preserve register state across the signal-return syscall boundary.
