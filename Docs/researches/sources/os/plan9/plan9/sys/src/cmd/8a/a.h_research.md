# File Research: sources/os/plan9/plan9/sys/src/cmd/8a/a.h

## Purpose
Main header for the Plan 9 386 assembler (`8a`). It defines assembler data structures, globals, constants, and prototypes.

## Key Structures
- `Sym`: symbol table entry with type, value, name, macro text, and object symbol slot.
- `Io`: input stack buffer used by file/include/macro processing.
- `Gen`: assembled operand representation, including offset, symbol, type, index, scale, string constant, and floating value.
- `Gen2`: instruction pair of `from` and `to` operands.
- `Hist`: source history entries for object debug/history records.

## Key Globals
Tracks input state (`fi`, `iostack`, `peekc`), symbol table (`hash`), include paths, current `pc`, pass number, output file, line number, macro definitions, and `Biobuf obuf`.

## Important Behavior
- Includes `../8c/8.out.h`, so assembler opcodes and operand codes are shared with the 386 compiler and linker.
- Declares parser, lexer, macro, object emission, and compatibility functions.
- Defines platform compatibility hooks imported from `../cc/compat.c`.

## Research Notes
This header is the contract among `a.y`, `lex.c`, shared compiler definitions, and Plan 9 object output encoding.
