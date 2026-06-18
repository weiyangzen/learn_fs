# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/arch/aarch64/sys/compat_sigpending.S

## Scope

AArch64 compatibility wrapper for old `sigpending`.

## Behavior

- Emits a warning reference recommending `<signal.h>`.
- Defines `PSEUDO(sigpending,compat_13_sigpending13)`.

## Dependencies And Invariants

- Uses the old integer signal-set ABI through the compatibility syscall.
