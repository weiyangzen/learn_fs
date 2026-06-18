# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/arch/m68k/sys/compat___sigreturn14.S

## Scope

m68k compatibility implementation of `__sigreturn14`.

## Behavior

- Defines explicit `ENTRY(__sigreturn14)`.
- Uses m68k trap-based signal-return path for `compat_16___sigreturn14`.

## Dependencies And Invariants

- Must preserve the user register image being restored by signal return.
