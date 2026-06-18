# File Research: sources/os/plan9/9front/sys/src/cmd/5a/a.y

This yacc grammar parses ARM assembly syntax for `5a` and emits object instructions through `outcode()`.

Main grammar behavior:
- Handles labels, variable/equate definitions, empty lines, instructions, and syntax-error recovery.
- Recognizes ARM data-processing instructions, `MVN`, `MOV*`, branches, `BX`, conditional branches, `SWI`, compare/test ops, `MOVM`, swap/exclusive ops, `RET`/`RFE`/`CLREX`, `TEXT`, `GLOBL`, `DATA`, `CASE`, `WORD`, floating-point ops, coprocessor `MCR`/`MRC`, multiply-long forms, `MULA`, `END`, and barriers `DMB`/`DSB`/`ISB`.
- Builds `Gen` operands for registers, register pairs, shifts, immediates, float constants, string constants, names, static symbols, PC-relative branches, indirect registers, and register lists.
- Encodes `MCR`/`MRC` directly as an `AWORD` with assembled coprocessor instruction bits.
- Supports ARM condition suffixes and S/P/W/U/F bit modifiers via `cond`.
- Supports expression evaluation with unary signs, complement, arithmetic, shifts, bitwise and/or/xor, variables, and parentheses.

Important operand forms:
- `rel` supports `offset(PC)`, unresolved labels, and resolved labels.
- `ximm` supports `$const`, `$oreg`, `$*$oreg`, `$"..."`, and floating immediates.
- `reglist` supports single registers, ranges, and comma-separated lists.
- `shift` encodes logical left/right, arithmetic right, and rotate syntax into `D_SHIFT` fields.
- `name` handles `offset(SB/SP/FP)`, symbol offsets, and `name<>+off(SB)` statics.

Dependencies and interactions:
- Tokens are produced by `lex.c` from its instruction/register table.
- Semantic actions call `outcode()` with the object opcode, condition byte, source operand, optional register, and destination operand.

Research relevance:
- Defines the accepted ARM assembly language for 9front’s `5a` toolchain and maps syntax to object-file operands.

Risk notes:
- Some range checks use `$$` before assignment in `rcon`, but then assign from parsed operands; this is old yacc-style code worth handling carefully.
- Coprocessor and shift encodings are hand-packed; errors would produce valid-looking but wrong instructions.
- Conditional branch and `B` condition handling relies on `lex.c:outcode()` normalization.
