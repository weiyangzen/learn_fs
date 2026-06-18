# File Research: sources/os/plan9/plan9/sys/src/cmd/6l/optab.c

## Purpose
Defines the AMD64 (`6l`) linker/assembler opcode table used by instruction selection and encoding. It maps Plan 9 abstract assembly opcodes (`A*`) to operand class prototypes, prefix requirements, and raw x86/x86-64 opcode byte sequences.

## Key Contents
- Operand prototype arrays such as `yxorl`, `ymovq`, `yjcond`, `ycall`, `yxmov`, and floating/SSE/MMX prototypes.
- `Optab optab[]`, the central dispatch table from opcode enum to:
  - accepted operand classes,
  - prefix class (`Px`, `Pw`, `Pe`, `Pm`, `Pf2`, etc.),
  - opcode bytes and ModR/M extension fields.
- `Optab* opindex[ALAST+1]`, later populated for fast lookup.

## Important Behavior
- Covers scalar integer, branch, call, return, stack, system, x87, MMX, SSE/SSE2, conditional move, and privileged instructions.
- Contains AMD64-specific variants such as `AMOVQ`, `AADDQ`, `ACALL`, `AJMP`, REX-width operations, and 64-bit save/restore forms.
- Encodes pseudo-ops (`ATEXT`, `ADATA`, `AGLOBL`, `ABYTE`, `ALONG`, `AQUAD`) alongside real machine instructions.
- Operand prototype arrays are tightly coupled to `span.c`’s `oclass()`, `doasm()`, and `Z*` encoding actions.

## Research Notes
This file is declarative but foundational: adding or changing an instruction requires matching enum names, assembler lexer names, operand class coverage, and `span.c` encoder support.
