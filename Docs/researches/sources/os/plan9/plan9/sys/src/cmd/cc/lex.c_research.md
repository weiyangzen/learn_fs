# File Research: sources/os/plan9/plan9/sys/src/cmd/cc/lex.c

This file is the compiler driver and lexical/input layer for the shared Plan 9 C compiler.

Key behavior:
- `main()` parses compiler flags, definitions, includes, output mode, and optional parallel compilation via `NPROC`.
- `compile()` sets output names, include paths, diagnostic/output buffers, optional external ANSI preprocessor invocation, and starts parsing.
- `yylex()` tokenizes identifiers, keywords, numbers, strings, character constants, operators, comments, and macro expansions.
- Handles UTF/rune-aware identifiers and string/character escapes through `getr()` and `escchar()`.
- Initializes symbols and base types in `cinit()`.
- Maintains include/file stack and source history for diagnostics with `newio()`, `newfile()`, `filbuf()`, and line-history formatting.
- Provides custom formatters for operators, types, source locations, node names, type-bit names, and indentation.
- Supplies arena-style allocation with `alloc()` and `allocn()` plus include-path registration.

Important details:
- Recognized debug flags control Acid output, pickle output, warnings, format checks, assembly, structure offsets, registerization, preprocessor selection, and other compiler internals.
- `L"..."` and `L'x'` constants are converted into target `TRune` values.
- Macro expansion is integrated by pushing expanded text onto the input stack.
- Output may be normal object/assembly, Acid declarations, or generated pickle C depending on flags.

Filesystem relevance:
- Indirect. Uses local source/include files and emits compiler outputs, but is not filesystem implementation logic.
