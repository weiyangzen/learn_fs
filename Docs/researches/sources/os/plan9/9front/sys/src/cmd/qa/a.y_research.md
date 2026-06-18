# File Research: sources/os/plan9/9front/sys/src/cmd/qa/a.y

Yacc grammar for the `qa` assembler. It parses labels, assignments, scheduler directives, instructions, operands, constants, expressions, and addressing modes, then emits encoded instructions through `outcode` or `outgcode`.

Key behavior:
- Supports integer/byte moves, floating load/store/convert/compare/add/MA, condition-register moves/ops, segment/MSR/SPR moves, branches, traps, rotate-and-mask, indexed load/store, NOP, WORD, END, TEXT/GLOBL, DATA, and RETURN forms.
- Builds `Gen` operands for registers, FP registers, condition registers, FPSCR, special registers, segment registers, immediates, string/floating constants, branches, names, and register-offset addresses.
- Resolves labels/variables and reports undefined labels on pass 2.
- Expression grammar supports unary signs/complement, arithmetic, shifts, bitwise ops, and parentheses.
- `mask` converts rotate-mask start/end fields into a 32-bit mask constant.

Integration points:
- Uses token values and operand constants from `a.h`/`q.out.h`.
- Output path is delegated to `outcode`/`outgcode`; lexical tokens come from the assembler lexer.

Risks:
- In `sreg: LR '(' con ')'`, the range check tests `$$` before assigning `$3`, so invalid-register diagnostics may be unreliable.
- Grammar is architecture-specific and tightly coupled to token classification from the lexer.
- Several optional comma productions accept legacy syntax that can make parse errors less explicit.
