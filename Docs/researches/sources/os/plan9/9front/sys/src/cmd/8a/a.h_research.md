# File Research: sources/os/plan9/9front/sys/src/cmd/8a/a.h

This is the shared header for the 386 assembler `8a`.

Key responsibilities:
- Includes Plan 9 libc/bio headers, the 386 object/opcode definitions from `../8c/8.out.h`, and shared compatibility definitions.
- Defines assembler constants for symbol tables, include depth, macro storage, IO buffering, and lexer sentinel values.
- Declares core assembler data structures:
  - `Sym` for symbols/macros/labels.
  - `Ref` for macro reference classes.
  - `Io` for nested file/input stack buffers.
  - `Gen` and `Gen2` for assembler operands.
  - `Hist` for source history records.
- Exposes global assembler state via `EXTERN`: debug flags, include paths, input stack, history, current pc/line/pass, symbol hash table, output buffer, and current token.
- Declares lexer, parser, macro, output, include, and assembly entry-point functions.

Integration points:
- Used by both `a.y` and `lex.c`.
- The `Gen` layout must match object emission expectations in `zaddr()` and linker object readers.
- The header bridges assembler syntax parsing to the shared 386 object format in `8.out.h`.

Risks and invariants:
- Fixed-size arrays such as `NSYM`, `NSYMB`, `NINCLUDE`, and `NMACRO` are traditional Plan 9 limits; overflow handling depends on code in shared lexer/macro bodies.
- `GETC()` directly manipulates global `fi`, so lexer correctness depends on consistent buffer state.
