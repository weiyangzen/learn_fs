# File Research: sources/os/plan9/plan9/sys/src/cmd/qa/a.h

Purpose: Shared definitions for the PowerPC assembler `qa`.

Key contents:
- Includes Plan 9 headers and `../qc/q.out.h`.
- Defines assembler limits, buffer sizes, hash sizes, macro limits, allocation macros, and input helpers.
- Structures: `Sym`, `Io`, `Gen`, `Hist`.
- Global state for debug flags, symbol hash, include paths, IO stack, line number, output file, pass number, pc, null address, history, macro defines, and output buffer.
- Declares lexer/parser, assembler, object emission, macro/preprocessor, include, history, memory hunk, and compatibility functions.

Dependencies and integration:
- Used by `a.y` and `lex.c`.
- Shares architecture constants with `qc/q.out.h`.

Risks and notes:
- Uses hunk allocator macros and many process-global variables.
- Compatibility prototypes import shared C compiler support.
