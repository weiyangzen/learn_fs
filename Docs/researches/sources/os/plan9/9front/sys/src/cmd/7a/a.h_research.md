# File Research: sources/os/plan9/9front/sys/src/cmd/7a/a.h

- Role: Central header for the ARM64 assembler `7a`.
- Includes Plan 9 runtime headers, ARM64 object/opcode definitions from `../7c/7.out.h`, and compiler compatibility definitions.
- Defines assembler structures: `Sym` for symbols/macros, `Io` for input stack buffers, `Gen` for parsed operands, and `Hist` for file history.
- Declares constants for symbol table size, buffers, include depth, macro count, lexer EOF/IGN sentinels, and hash size.
- Declares global assembler state: lexer input, symbol hash, debug flags, include paths, macro/input stacks, line number, pass number, current `pc`, output buffer, and history lists.
- Prototypes cover two-pass assembly, lexer/parser entry points, symbol handling, macro/preprocessor support, file history, object emission, and diagnostics.
