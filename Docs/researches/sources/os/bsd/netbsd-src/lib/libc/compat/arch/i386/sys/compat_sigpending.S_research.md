# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/arch/i386/sys/compat_sigpending.S

## Scope

i386 compatibility implementation of old `sigpending`.

## Behavior

- Uses `_SYSCALL(sigpending,compat_13_sigpending13)`.
- Stores returned old integer mask through the caller-provided pointer.
- Clears return register for success.

## Dependencies And Invariants

- Adapts old integer mask syscall result to modern pointer-return function shape.
