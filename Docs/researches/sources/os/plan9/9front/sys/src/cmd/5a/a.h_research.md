# File Research: sources/os/plan9/9front/sys/src/cmd/5a/a.h

This header defines shared state and interfaces for the ARM assembler `5a`.

Key contents:
- Includes Plan 9 user, libc, bio, ARM object format `../5c/5.out.h`, and common compiler compatibility support.
- Defines constants for alignment, symbol counts, buffer sizes, include nesting, macro counts, hash size, and token helpers.
- Defines `Sym`, assembler symbol records with macro text, value, type, name, and object symbol index.
- Defines input buffering structures: `fi` and `Io`.
- Defines symbol cache `h[NSYM]` for object-file name references.
- Defines `Gen`, the assembler’s generic operand representation: symbol, offset, type, register, name, float value, and string constant.
- Defines `Hist` for file/line history.
- Declares global assembler state: debug flags, symbol hash, include paths, macro/io stacks, current line, pass number, PC, output file, object character/string, and `Biobuf obuf`.
- Declares parser, lexer, macro, object emission, history, include, error, and assembly-entry functions.

Dependencies and interactions:
- Used by `a.y` and `lex.c`.
- Shares operand and opcode constants with `5c/5.out.h`, ensuring assembler output matches compiler/linker expectations.

Research relevance:
- This is the central ABI between assembler grammar, lexer/macro preprocessor, and object writer.

Risk notes:
- Many globals are shared through `EXTERN`; initialization order in `lex.c:cinit()` matters.
- `Gen.sval` is fixed at 8 bytes via `NSNAME`, matching object format assumptions.
