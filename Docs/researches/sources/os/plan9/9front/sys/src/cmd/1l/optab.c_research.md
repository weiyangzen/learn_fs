# File Research: sources/os/plan9/9front/sys/src/cmd/1l/optab.c

Instruction metadata table for the `1l` 68000 linker/emitter.

Key contents:
- Defines `optab[]`, indexed by Plan 9 opcode enum value.
- Each entry maps an assembler opcode to:
  - optional floating/integer alternate opcode,
  - source and destination stack-size effects,
  - emitter `optype`,
  - up to four opcode words/templates.
- Covers integer arithmetic, branches, bit operations, compares, moves, shifts, multiply/divide, 68881 floating-point operations, FP branches/DBcc, movem/fmovem, traps, pseudo-ops, and unimplemented placeholders.
- Defines `mmsize[]`, a size table by emitter operation type.

Role in system:
- `asm.c` uses `optype` to choose instruction encoding logic and opcode templates.
- `dostkoff` uses stack-size metadata to track stack pointer effects.
