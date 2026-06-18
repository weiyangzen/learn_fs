# File Research: sources/os/plan9/plan9/sys/src/cmd/8a/lex.c

## Purpose
Main driver, lexical initialization, opcode/register table, and object emission logic for the 386 assembler.

## Key Functions
- `main()` parses flags, supports parallel assembly of multiple files on non-Windows systems, and dispatches `assemble()`.
- `assemble()` establishes output path, include paths, two assembler passes, predefined macros, history output, and final cleanup.
- `cinit()` initializes assembler state, symbol table, null operand, predefined symbols, opcodes, and working directory.
- `checkscale()` validates scaled-index factors.
- `zname()` emits object-file symbol name records.
- `zaddr()` serializes an operand using `T_*` compact address flags.
- `outcode()` emits instruction records and maintains object symbol cache entries.
- `outhist()` emits source path/history records.

## Opcode/Register Table
`itab[]` maps textual names to parser token classes and opcode/register values:
- special registers: `SP`, `SB`, `FP`, `PC`;
- byte/general/floating/segment/control/debug/task registers;
- integer, branch, stack, string, floating, conditional move, and system opcodes.

## Important Behavior
- Uses two passes: pass 1 computes labels/PCs; pass 2 emits object records.
- Object records share opcode/address enums with `8.out.h`.
- Includes shared preprocessor/macro/compatibility bodies from `../cc/lexbody`, `../cc/macbody`, and `../cc/compat`.

## Research Notes
This file is where assembler text names become shared Plan 9 object opcodes.
