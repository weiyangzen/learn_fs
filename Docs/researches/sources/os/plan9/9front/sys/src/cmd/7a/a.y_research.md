# File Research: sources/os/plan9/9front/sys/src/cmd/7a/a.y

- Role: Yacc grammar for the ARM64 assembler syntax accepted by `7a`.
- Defines semantic value types for symbols, integer constants, floating constants, string constants, and `Gen` operands.
- Instruction grammar maps token classes (`LTYPE*`, `LMOVK`, `LDMB`, `LSTXR`, etc.) to `outcode()` or `outcode4()` calls with parsed operands and optional middle register fields.
- Covers ARM64 integer ALU, MOV/MOVK/MOVZ/MOVN, branches, conditional branches, compare/test aliases, conditional select/set, test-bit branches, system instructions, barriers/hints, load/store exclusive, text/global/data directives, word directives, floating point, fused multiply-add, SIMD/vector operands, pair moves, and END.
- Operand grammar handles immediates, float/string constants, labels/branches, static/extern/auto/param names, SP/SB/FP/PC pointer spaces, pre/post-indexed memory, register-offset addressing, shifts, extended registers, system-register args, scalar/vector/floating registers, vector lanes, and vector register sets.
- Expression grammar supports unary sign/complement and binary arithmetic, shifts, bitwise ops, and parentheses.
- Performs validation for register numbers and shift ranges in grammar actions.
- Produces Plan 9 object records indirectly through the output routines in `lex.c`.
