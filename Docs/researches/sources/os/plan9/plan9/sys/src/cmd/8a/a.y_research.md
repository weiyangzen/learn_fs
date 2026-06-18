# File Research: sources/os/plan9/plan9/sys/src/cmd/8a/a.y

## Purpose
Yacc grammar for the 386 assembler syntax accepted by `8a`.

## Key Grammar Areas
- `line` handles labels, blank statements, instructions, and parse errors.
- `inst` handles symbol assignment and instruction classes (`LTYPE0`, `LTYPE1`, `LTYPE2`, `LTYPE3`, `LTYPE4`, `LTYPER`, `LTYPED`, `LTYPET`, etc.).
- `spec1` through `spec8` describe special forms:
  - `DATA`,
  - `TEXT`,
  - `JMP/CALL`,
  - `NOP`,
  - shifts,
  - `MOVW/MOVL` with segment operands,
  - variable operand-count forms,
  - `GLOBL`.
- Operand rules cover registers, immediates, memory, names, branches, scaled index addressing, static symbols, and offsets.
- Expression grammar supports arithmetic, shifts, bitwise operators, unary sign, complement, constants, and assembler variables.

## Important Behavior
- Labels are resolved through a two-pass assembler model; unresolved labels during pass 2 are reported.
- Branch operands may be PC-relative constants or symbolic labels.
- Address forms support Plan 9 syntax such as `name+off(SB)`, `name<>+off(SB)`, `off(REG)`, and scaled indexed addressing.
- `checkscale()` validates index scales of 1, 2, 4, or 8.

## Research Notes
This grammar converts textual Plan 9 assembly into `Gen2` records emitted by `outcode()` in `lex.c`.
