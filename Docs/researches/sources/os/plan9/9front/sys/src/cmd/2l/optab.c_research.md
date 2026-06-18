# File Research: sources/os/plan9/9front/sys/src/cmd/2l/optab.c

Purpose: declarative instruction encoding table for the 68020 linker.

Key contents:
- `optab[]` is indexed by opcode enum value from `2.out.h`; `main()` checks index/opcode phase consistency.
- Each populated row supplies:
  - assembler opcode,
  - optional alternate FPU opcode (`fas`) for integer-representable FP constants,
  - source/destination extension sizes,
  - encoding class `optype`,
  - up to four raw opcode words used by `asmins()`.
- Covers integer arithmetic, moves, branches, DBcc, bit-field operations, FPU arithmetic/conversions/moves/branches, jump/call, traps, tests, MOVEM/FMOVEM, MOVES, CASEW/BCASE, and pseudo-ops.
- `mmsize[]` maps encoding class to minimum instruction size for span calculation.

Research notes:
- Rows with sparse/unimplemented opcodes contain only `{ AOP }`; `asmins()` diagnoses unimplemented combinations when encountered.
- `optype` is the switch discriminator in `asm.c`; changing an encoding class requires corresponding `asmins()` support.
- Source/destination size fields drive immediate/FPU constant extension emission and span size prediction.
