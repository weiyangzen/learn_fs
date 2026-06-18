# File Research: sources/os/plan9/9front/sys/src/cmd/ka/a.h

Shared header for the 9front `ka` assembler. It includes Plan 9 runtime headers, `k.out.h`, and C compiler compatibility definitions, then declares assembler-wide structures and globals.

Core structures are `Sym` for symbols/macros, `Io` for input stack buffers, `Gen` for parsed operands/addresses, and `Hist` for source history. Macros define buffer sizes, hash sizes, EOF/IGN sentinels, `GETC`, and assembler constants.

The header declares lexer/parser, macro preprocessor, include handling, history, symbol lookup, output encoding, and assembly driver functions used across the assembler implementation.
