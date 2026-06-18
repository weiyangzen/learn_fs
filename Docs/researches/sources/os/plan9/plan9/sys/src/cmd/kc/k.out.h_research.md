# File Research: sources/os/plan9/plan9/sys/src/cmd/kc/k.out.h

This header defines the Plan 9 SPARC object-code ABI used by the assembler, compiler, and linker. It includes register constants, opcode enum values, operand type/name constants, and IEEE double layout.

Register definitions identify fixed roles: `REGZERO`, `REGSP`, `REGSB`, `REGEXT`, `REGRET`, `REGTMP`, `REGLINK`, `REGARG`, and floating return/external/special constant registers.

`enum as` lists all SPARC backend opcodes and pseudo-ops, including integer operations, condition branches, floating branches/arithmetic/conversions, moves, traps, `TEXT`, `DATA`, `GLOBL`, `HISTORY`, `NAME`, `WORD`, and object metadata records.

Operand constants distinguish names (`D_EXTERN`, `D_STATIC`, `D_AUTO`, `D_PARAM`) and types (`D_BRANCH`, `D_OREG`, `D_ASI`, `D_CONST`, `D_FCONST`, `D_SCONST`, `D_REG`, `D_FREG`, `D_CREG`, `D_PREG`, `D_FILE`). This file is the synchronization point for `ka`, `kc`, and object consumers.
