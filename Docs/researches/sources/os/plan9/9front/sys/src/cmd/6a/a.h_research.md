# File Research: sources/os/plan9/9front/sys/src/cmd/6a/a.h

This header defines the shared assembler state and data structures for `6a`, the amd64 assembler.

Key elements:
- `Sym` stores assembler symbols, macro text, values, lexical type, and object-file symbol cache index.
- `Gen` is the assembler operand structure with floating/string constants, offset, symbol, type, index register, and scale.
- `Gen2` packages source and destination operands for grammar reductions.
- `Io` and `Hist` track input streams and source history.
- Global state includes debug flags, symbol hash, `-D` definitions, include directories, input stack, line number, output path, program counter, token text, architecture identity, and output buffer.
- Function prototypes cover input/macro handling, parsing, symbol lookup, operand/object encoding, history emission, diagnostics, and assembly entry points.

Dependencies and integration:
- Includes amd64 object definitions from `../6c/6.out.h`.
- Includes shared compiler compatibility declarations.

Research notes:
- This is the contract among `a.y`, `lex.c`, generated parser code, and shared lexer/macro bodies.
