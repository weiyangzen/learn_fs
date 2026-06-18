# File Research: sources/os/plan9/plan9/sys/src/9/rb/init9.s

Tiny MIPS userland bootstrap assembly for Plan 9.

Key responsibilities:
- `_main` sets static base register `R30`.
- Places `boot(SB)` and a pointer to arguments onto the stack frame.
- Calls `startboot(SB)`.

Role:
- Entry shim for the initial user boot program.

Notable risks:
- Assumes exact Plan 9 MIPS calling convention and initial stack layout.
