# File Research: sources/os/plan9/plan9/sys/src/cmd/5a/a.h

Shared header for the Plan 9 ARM assembler `5a`.

Key contents:
- Includes `../5c/5.out.h` for ARM object/instruction definitions.
- Defines assembler constants, buffered input state, symbol table structures, operand `Gen`, and history records.
- Declares global assembler state: symbols, include paths, pass number, output file, PC, current token, line number, and output buffer.
- Declares lexer, parser, macro, I/O, object emission, history, and compatibility functions.

Notes:
- The assembler is a two-pass tool sharing object ABI with `5c` and the linker.
