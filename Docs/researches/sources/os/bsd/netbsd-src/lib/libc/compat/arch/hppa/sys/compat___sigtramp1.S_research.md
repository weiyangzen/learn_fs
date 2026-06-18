# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/arch/hppa/sys/compat___sigtramp1.S

## Scope

HPPA legacy signal trampoline.

## Behavior

- Defines `ENTRY_NOPROFILE(__sigtramp_sigcontext_1,0)`.
- Reconstructs/uses the old signal frame and enters the signal-return path.
- Contains HPPA-specific instruction sequencing for trampoline execution.

## Dependencies And Invariants

- Stack layout, register preservation, and trampoline entry alignment are ABI-critical.
