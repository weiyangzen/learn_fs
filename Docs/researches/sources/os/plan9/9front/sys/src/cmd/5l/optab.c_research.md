# File Research: sources/os/plan9/9front/sys/src/cmd/5l/optab.c

This file defines the ARM linker opcode-selection table `optab[]`.

Key elements:
- Each `Optab` row maps an opcode plus operand classes to:
  - an emission recipe type used by `asmout()`,
  - instruction size in bytes,
  - optional base register parameter,
  - flags such as `LFROM`, `LTO`, `LPOOL`, `V4`, and `VFP`.
- Covers ARM data processing, constants, shifts, branches, SWI, words, byte/half/word loads/stores, MOVM, SWP/LDREX/STREX, RFE/CLREX, barriers, old FPA, VFP, case dispatch, and address-relocation forms.
- Final row `{ AXXX, ... }` terminates the table.

Dependencies and integration:
- Consumed by `buildop()` and `oplook()` in `span.c`.
- Emission recipe numbers are interpreted by `asmout()` in `asm.c`.

Notable behavior:
- Long-offset or relocatable forms deliberately expand to multi-instruction sequences.
- ARMv4 and VFP rows can be disabled depending on debug flags processed in `buildop()`.
- Some aliases share opcode ranges after `buildop()` copies `oprange[]` entries.

Research notes:
- This table is declarative machine-code policy for `5l`.
- Correctness depends on consistency among operand classes in `l.h`, classification in `span.c`, and recipe handling in `asm.c`.
