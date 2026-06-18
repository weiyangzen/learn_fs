# File Research: sources/os/plan9/plan9/sys/src/cmd/va/a.y

Yacc grammar for the MIPS assembler frontend.

Main contents:
- Token and semantic value declarations for instruction classes, registers, constants, labels, names, and addressing modes.
- Grammar for labels, variable assignments, scheduling directives, and instruction statements.
- Instruction forms cover arithmetic/immediate ops, NOR, load/store, MOVW/MOVV/MOVD/MOVF, multiply/divide, jumps, branches, TEXT/GLOBL/DATA, floating-point ops, coprocessor branches, WORD, NOP, BREAK/CACHE overload, and special ops.
- Addressing grammar builds `Gen` operands for registers, immediates, memory references, branch targets, static/external names, HI/LO, FP regs, coprocessor regs, and string/float constants.
- Constant expression grammar supports unary and binary arithmetic/bitwise operators.

Output:
- Semantic actions call `outcode` with assembled opcode and operands.
- Undefined labels become branch operands and are diagnosed on pass 2.
- Some register/operand validation is minimal and defers work to later stages.

This file defines accepted assembly syntax and operand lowering into the assembler’s `Gen` representation.
