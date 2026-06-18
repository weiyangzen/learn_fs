# File Research: sources/os/plan9/plan9/sys/src/cmd/va/a.h

Shared header for the Plan 9 MIPS assembler (`va`).

Defines:
- Core assembler data structures: `Sym`, `Io`, `Gen`, and `Hist`.
- Buffer, hash table, include, macro, hunk, and parser constants.
- Global assembler state via `EXTERN`: input buffer, symbol hash, include paths, history, line number, output file, pass number, pc, current token, debug flags, and output `Biobuf`.
- Parser/lexer/codegen function declarations.
- Compatibility function declarations from the compiler compatibility layer.
- OS type constants matching the C compiler.

This is the central state and API header for `a.y` and `lex.c`.
