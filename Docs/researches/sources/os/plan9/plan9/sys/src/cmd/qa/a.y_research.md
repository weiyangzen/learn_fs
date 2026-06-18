# File Research: sources/os/plan9/plan9/sys/src/cmd/qa/a.y

Purpose: Yacc grammar for the PowerPC assembler.

Key behavior:
- Defines tokens for instruction classes, registers, constants, names, labels, string constants, and floating constants.
- Handles labels, variable assignments, scheduler directives, and instructions.
- Grammar covers integer loads/stores, floating loads/stores, FPSCR/condition register moves, arithmetic/logical/shift/unary ops, multiply-accumulate, immediates, condition-register ops, branch forms, traps, floating ops, compares, rotate/mask, multiword moves, indexed ops, NOP, WORD, END, TEXT/GLOBL, DATA, and RETURN.
- Defines addressing forms: registers, special registers, condition regs, FPSCR fields, segment regs, indexed addressing, static/name addressing, stack/base/frame pointers, constants and expressions.
- Emits instructions via `outcode` and `outgcode`.

Dependencies and integration:
- Includes `a.h`; generated parser consumed by `lex.c`.
- Uses `pc`, `pass`, `nullgen`, and PowerPC operand encodings from `q.out.h`.

Risks and notes:
- Some register range diagnostics refer to `$$` before assignment in `sreg` rule, likely a bug.
- Undefined label errors happen on pass 2.
- Mask generation validates 0..31 ranges.
