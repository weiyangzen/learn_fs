# File Research: sources/os/plan9/plan9/sys/src/cmd/vc/v.out.h

Purpose: MIPS object/instruction definitions for the Plan 9 `vc` backend.

Contents:
- Defines symbol-name length, symbol cache size, and register count.
- Defines text flags and named machine registers such as zero, return, stack, static base, link, and floating constants.
- Declares `enum as` instruction/pseudo-op numbers.
- Defines address type/name constants such as `D_BRANCH`, `D_OREG`, `D_EXTERN`, `D_AUTO`, `D_CONST`, `D_FREG`, `D_LO`, and `D_HI`.
- Defines archive symbol marker `SYMDEF`.
- Defines `Ieee`, Plan 9’s simulated IEEE double representation.

Integration points:
- Included by `gc.h`, used by every backend file.
- `enam.c` must match `enum as` order.
- Object writing in `swt.c` serializes these opcode and address type values.

Risks:
- This is an object format contract; numeric changes affect assembler/linker compatibility.
