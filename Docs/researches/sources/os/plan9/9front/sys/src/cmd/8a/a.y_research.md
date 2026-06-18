# File Research: sources/os/plan9/9front/sys/src/cmd/8a/a.y

This yacc grammar defines the 386 assembly language accepted by `8a`.

Key responsibilities:
- Parses labels, variable definitions, instruction lines, and expression syntax.
- Maps lexer token families such as `LTYPE0`, `LTYPE3`, `LTYPED`, `LTYPET`, and `LTYPEC` to instruction operand templates, then calls `outcode()`.
- Handles special pseudo-instructions:
  - `DATA name/size, imm`
  - `TEXT mem, [flags,] frame`
  - `GLOBL mem, [flags,] size`
  - `JMP/CALL` forms
  - `NOP`, shifts, MOVW/MOVL segment forms, SIMD compare/shuffle forms, and `CMPXCHG8B`.
- Builds `Gen` operands for registers, immediates, branches, memory references, indexed addressing, symbol references, constants, string constants, floating constants, and two-part constants.
- Supports arithmetic/bitwise constant expressions with yacc precedence.

Integration points:
- Depends on tokens and semantic types from `a.h`/`lex.c`.
- Emits parsed instructions through `outcode(int, Gen2*)`.
- Uses `pc` and pass number to resolve labels and detect undefined labels on pass 2.

Risks and invariants:
- Scale validation is delegated to `checkscale()` and permits only 1, 2, 4, or 8.
- Some syntax-specific constraints are enforced in actions, for example double-precision shifts and moves cannot already have conflicting index fields.
- Branch operands may carry unresolved symbols during pass 1 and become concrete during pass 2.
