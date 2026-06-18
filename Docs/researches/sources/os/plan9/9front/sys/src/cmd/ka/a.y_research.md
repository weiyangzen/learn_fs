# File Research: sources/os/plan9/9front/sys/src/cmd/ka/a.y

Yacc grammar for the `ka` assembler frontend. It defines token value types, precedence for assembler expressions, instruction grammar, address grammar, and semantic actions that emit assembled instructions via `outcode`.

The instruction rules cover SPARC-like integer loads/stores, floating-point and coprocessor moves, arithmetic/logical/shift forms, branches, calls/jump-and-link, traps, state-register moves, flush, floating/coprocessor operations, `TEXT`, `DATA`, `RETURN`, `NOP`, and `END`.

Operand nonterminals build `Gen` records for registers, special registers, coprocessor/floating registers, immediates, string/float constants, branches, offsets, stack/static names, and register-relative addressing. Expression rules support constants, variables, unary operations, arithmetic, shifts, and bitwise operators.
