# File Research: sources/os/plan9/9front/sys/src/cmd/1a/a.h

Shared header for the Plan 9 `1a` assembler front end, targeting Motorola 68000-family object code.

Key contents:
- Includes Plan 9 libc/Bio support, `../2c/2.out.h` opcode/address definitions, and compiler compatibility helpers.
- Defines assembler limits, buffered input macros, hash sizes, include/macro limits, and parser constants.
- Declares core data structures: `Sym`, `Ref`, `Io`, `Addr`, `Gen`, `Gen2`, and `Hist`.
- Declares all assembler globals for input state, include paths, symbol table, histories, pass number, current PC, output file, and object output buffer.
- Provides prototypes for parsing, macro/preprocessor handling, object serialization, symbol/history output, diagnostics, and initialization.

Role in system:
- This is the contract between the yacc grammar, lexer/preprocessor, and object writer in `cmd/1a`.
