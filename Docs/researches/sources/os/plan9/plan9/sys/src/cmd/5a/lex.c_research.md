# File Research: sources/os/plan9/plan9/sys/src/cmd/5a/lex.c

Lexer, driver, symbol initialization, and object emission support for ARM assembler `5a`.

Key behavior:
- `main` parses assembler options, supports parallel assembly of multiple files on non-Windows systems, and selects ARM or Thumb output suffix.
- `assemble` runs pass 1 and pass 2, handles include paths and `-D` macros, creates output, and emits history.
- `itab` maps registers, condition suffixes, addressing suffixes, mnemonics, and directives to parser tokens/opcodes.
- `cinit` initializes symbols and assembler globals.
- `zname`, `zaddr`, `outcode`, and `outhist` serialize names, operands, instructions, and file history to the object stream.
- Includes shared C compiler lexer/macro/compat bodies.

Notes:
- Converts `B.cond` into the corresponding conditional branch opcode in `outcode`.
- Maintains a small object symbol table with `ANAME` records.
