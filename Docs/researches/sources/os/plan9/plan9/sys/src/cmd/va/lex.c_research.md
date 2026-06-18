# File Research: sources/os/plan9/plan9/sys/src/cmd/va/lex.c

Assembler driver, lexer initialization, opcode table, and object emission support for `va`.

Main behavior:
- `main` parses assembler options, sets target char/string (`v`/`mips` or little-endian `0`/`spim`), include paths, defines, output file, and parallel assembly for multiple inputs.
- `assemble` derives output filename, configures include paths, creates output, runs two assembler passes, emits history, and finalizes object output.
- `itab[]` maps register names, special names, and instruction mnemonics to parser token types and opcode values.
- `cinit` initializes null operand state, error/input globals, hash table, predefined symbols, and current pathname.
- `syminit`, `isreg`, and `cclean` provide assembler support hooks.
- `zname` emits symbol-name records.
- `zaddr` serializes `Gen` operands into object format.
- `outcode` emits instructions on pass 2, assigns symbol table slots, records line number and scheduling flag, and advances pc on pass 1/2.
- `outhist` emits source path history records.
- Includes shared compiler lexer, macro, and compatibility bodies.

This file bridges parsing to Plan 9 object output for the MIPS assembler.
