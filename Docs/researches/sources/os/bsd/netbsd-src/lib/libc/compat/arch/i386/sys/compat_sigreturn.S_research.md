# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/arch/i386/sys/compat_sigreturn.S

## Scope

i386 compatibility wrapper for old `sigreturn`.

## Behavior

- Customizes profiling entry behavior to preserve registers.
- Defines `PSEUDO(sigreturn,compat_13_sigreturn13)`.

## Dependencies And Invariants

- The signal-return path must not disturb user register state while entering the kernel.
