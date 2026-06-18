# File Research: sources/os/plan9/9front/sys/src/cmd/2a/a.h

Purpose: shared declarations for the 68020 assembler `2a`.

Key contents:
- Includes Plan 9 libc/Bio headers, the shared 68020 object ISA header `../2c/2.out.h`, and common compiler compatibility support.
- Defines assembler constants for symbol table size, hash buckets, include depth, macro depth, buffers, EOF/IGN sentinels, and lexer input macro `GETC()`.
- Declares core data structures: `Sym`, `Ref`, `Io`, `Addr`, `Gen`, `Gen2`, and `Hist`.
- `Gen` extends `Addr` with floating/string constants, indexed-address displacement, scale, field metadata, and secondary type.
- Declares global assembler state for lexer, macro/include stack, output file, symbols, histories, current pass, PC, and object output buffer.
- Prototypes assembler phases and helpers: initialization, parsing, lexing, macro handling, symbol lookup, object record output, history output, and file assembly.

Research notes:
- This header is the contract between `a.y`, `lex.c`, and common `../cc/lexbody`/`macbody`.
- Address types and opcode IDs intentionally match `2c/2.out.h`, so assembler and compiler produce compatible `.2` object streams.
