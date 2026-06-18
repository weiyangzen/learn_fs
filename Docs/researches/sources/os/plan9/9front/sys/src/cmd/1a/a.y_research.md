# File Research: sources/os/plan9/9front/sys/src/cmd/1a/a.y

Yacc grammar for the Plan 9 `1a` assembler.

Key responsibilities:
- Parses labels, variable definitions, instruction forms, operands, addressing modes, constants, expressions, branch targets, `DATA`, `TEXT`, and bit-field instruction syntax.
- Emits object records through `outcode` during parse actions.
- Tracks label definitions and reports duplicate or undefined labels on pass 2.
- Builds `Gen2` source/destination operand pairs for instruction classes `LTYPE1` through `LTYPEB`.
- Supports 68000 addressing syntax including registers, indirect, predecrement, postincrement, `SB/SP/FP/PC/TOS`, static `<>`, constants, string constants, and floating constants.
- Evaluates integer expressions in grammar actions with arithmetic, shifts, and bitwise operators.

Notable details:
- The assembler is two-pass; branch symbols may remain unresolved in pass 1 but are diagnosed in pass 2.
- `TEXT` and `DATA` have specialized productions to capture frame/displacement metadata.
