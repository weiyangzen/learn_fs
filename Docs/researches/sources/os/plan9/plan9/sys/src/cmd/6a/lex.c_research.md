# File Research: sources/os/plan9/plan9/sys/src/cmd/6a/lex.c

This file is the amd64 assembler driver, symbol/opcode initializer, object encoder, and lexer support glue. `main` parses options, supports parallel assembly on non-Windows hosts using `NPROC`, and delegates each file to `assemble`.

`assemble` derives the output `.6` file name, configures include paths, opens the object output, and runs the assembler in two passes. Pass 1 resolves labels and symbols; pass 2 emits history and instruction records.

The large `itab` table maps register names, special pseudo-registers (`SP`, `SB`, `FP`, `PC`), integer/floating/media registers, segment/control/debug/task registers, opcodes, pseudo-ops (`TEXT`, `DATA`, `GLOBL`, `END`, `MODE`), condition aliases, x87, MMX, and SSE instructions into parser token classes and opcode enum values.

`cinit` initializes symbols and null operands. `zname`, `zaddr`, and `outcode` emit Plan 9 object records, including compact address encodings, symbol table slots, 64-bit offsets, floating constants, string constants, and source history.

The file includes shared C compiler lexer/macro/compat bodies, so assembler preprocessing and macro behavior align with the broader Plan 9 compiler suite.
