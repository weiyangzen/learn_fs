# File Research: sources/os/plan9/plan9/sys/src/cmd/ka/a.y

This is the yacc grammar for the SPARC assembler. It parses Plan 9 assembly source into object-code records by calling `outcode(op, from, reg, to)`.

The grammar recognizes labels, symbol assignments, scheduler directives, SPARC integer loads/stores, floating-point loads/stores/operations, coprocessor operations, branches, calls/jumps, traps, state-register moves, `TEXT`, `GLOBL`, `DATA`, `RETURN`, `END`, `NOP`, and `WORD`/unimplemented forms.

Operand grammar builds `Gen` values for registers, floating registers, coprocessor registers, processor-state registers, immediates, string/floating constants, branch targets, SB/SP/FP-relative names, static names, ASI references, indexed addressing, and PC-relative expressions.

The file is tightly coupled to token definitions from `y.tab.h`, opcode numbers from `k.out.h`, and symbol state from `a.h`. It is intentionally two-pass: undefined labels produce pass-sensitive errors, and label values are assigned from `pc`.
