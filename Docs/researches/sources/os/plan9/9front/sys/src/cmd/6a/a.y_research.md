# File Research: sources/os/plan9/9front/sys/src/cmd/6a/a.y

This file is the yacc grammar for the amd64 assembler `6a`.

Key elements:
- Defines token value types for symbols, integers, floats, string constants, operands, and operand pairs.
- `prog` and `line` parse labels, statements, blank lines, and error recovery.
- `inst` handles symbol assignment and dispatches instruction token classes to specialized operand grammars.
- Operand pair nonterminals normalize instruction forms into `Gen2`.
- Special grammar forms handle:
  - `DATA` as `name/size, immediate`,
  - `TEXT`/`GLOBL` as memory plus flags/frame,
  - `JMP`/`CALL` style relative or indirect targets,
  - `NOP`,
  - shifts with optional double-precision register suffix,
  - MOVW/MOVL with optional index suffix,
  - SIMD compare/shuffle immediate forms,
  - far returns with optional immediate.
- Operand grammar covers registers, immediates, strings, floats, memory addressing, symbol-relative names, static `<>` names, SP/FP/SB/PC pointers, and constant expressions.

Dependencies and integration:
- Emits object records by calling `outcode()`.
- Uses `checkscale()` for x86 addressing scale validation.
- Uses `pc` for PC-relative branches and `pass` for undefined-label diagnostics.

Notable behavior:
- Expressions support unary plus/minus/complement and binary arithmetic, shifts, and bitwise operators.
- Indexed memory addressing supports base plus index times scale.
- Undefined labels are tolerated in pass 1 and rejected in pass 2.

Research notes:
- This grammar converts Plan 9 assembler syntax into the compact `Gen` representation later serialized by `lex.c`.
