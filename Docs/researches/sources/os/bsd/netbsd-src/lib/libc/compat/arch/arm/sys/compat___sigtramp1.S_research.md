# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/arch/arm/sys/compat___sigtramp1.S

## Scope

ARM legacy signal trampoline.

## Behavior

- Defines `ENTRY(__sigtramp_sigcontext_1)`.
- Adapts the old signal frame and invokes the compatibility signal-return path.

## Dependencies And Invariants

- Stack frame layout and saved register locations must match old ARM signal delivery ABI.
