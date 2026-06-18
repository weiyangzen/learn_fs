# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/arch/alpha/sys/compat___sigtramp1.S

## Scope

Alpha old signal trampoline compatibility code.

## Behavior

- Provides the legacy signal trampoline entry used to return from old signal handlers.
- Bridges the user signal frame back into the kernel’s compatibility signal-return mechanism.

## Dependencies And Invariants

- Highly ABI-sensitive: stack/register layout must match old Alpha signal frame expectations.
