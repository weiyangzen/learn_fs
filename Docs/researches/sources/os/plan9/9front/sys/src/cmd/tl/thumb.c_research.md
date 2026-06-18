# File Research: sources/os/plan9/9front/sys/src/cmd/tl/thumb.c

Read completely: 1636 lines, 39963 bytes.

This implements Thumb instruction support for the `tl` linker. It classifies Thumb operands, defines the Thumb optab, builds optab ranges, emits 16-bit Thumb instruction sequences, handles long branches and literal-pool expansions, counts emitted opcode sizes, and includes a debug Thumb disassembler.

Key behavior:
- `thumbaclass` maps Plan 9 addressing modes into Thumb classes, computes branch displacement classes, sets alignment needs for long branches, and handles function pointer interworking/T-bit adjustments.
- `thumboptab` lists accepted instruction forms, emitted sizes, emitter cases, and literal-pool flags.
- `thumbasmout` emits cases for arithmetic, moves, loads/stores, branch/call expansions, large constants, stack-relative forms, `AWORD`, and `ADWORD`.
- Helper functions validate low/high register use, alignment multiples, immediate ranges, and Thumb opcode bit encodings.
- `dis` decodes emitted 16-bit instructions for debug output.

Dependencies:
- Includes `l.h`, shares `ocmp`, `isbranch`, `fninc`, `fnpinc`, literal-pool state, `instoffset`, output buffer pointers, and architecture constants with the linker backend.

Reliability notes:
- The code contains deliberate diagnostics for unsupported ARM-only operand classes in Thumb mode.
- Some large-immediate construction uses `rand()` to choose a decomposition, which can make emitted instruction sequences non-obvious though still intended to be equivalent.
