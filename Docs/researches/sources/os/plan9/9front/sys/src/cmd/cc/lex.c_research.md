# File Research: sources/os/plan9/9front/sys/src/cmd/cc/lex.c

Main driver, input manager, lexer, symbol initialization, include handling, and formatter support for the Plan 9 C compiler.

Key behavior:
- `main` initializes compiler type tables, globals, debug flags, include paths, and command-line options.
- Supports parallel compilation of multiple files using `NPROC`, while avoiding interleaved stdout for acid/pickle output.
- `compile` chooses output file names, configures include paths, opens output buffers, optionally runs `/bin/cpp`, and invokes `yyparse`.
- `newio`, `pushio`, `newfile`, and `filbuf` manage nested file/macro input streams.
- `lookup` and `slookup` maintain the compiler symbol hash table.
- `yylex` handles identifiers, keywords, macros, comments, string/rune literals, numeric constants, operators, and Plan 9 extensions such as binary integer constants.
- Numeric scanning chooses token/type by suffix, signedness, decimal-vs-nondecimal rules, and target widths; emits truncation/widening warnings.
- `escchar` decodes character escapes, including non-ANSI long hex/octal forms used by this compiler.
- `cinit` builds primitive type nodes, installs keywords, initializes `.string`, current path, and custom formatters.
- `Oconv`, `Lconv`, `Tconv`, `FNconv`, `Qconv`, and `VBconv` implement compiler-specific formatting for diagnostics and debug output.
- `setinclude` appends unique include directories from space-separated path strings.

Dependencies:
- Includes `cc.h` and parser tokens from `y.tab.h`.
- Depends on macro expansion routines from included macro support, parser entry `yyparse`, code cleanup `gclean`, and Plan 9 libc/`Bio` routines.

Research notes:
- This file is the compiler’s process and lexical boundary.
- `Lconv` reconstructs include and `#line` history for diagnostics.
- Macro expansion is integrated into the lexer by pushing expanded text onto the same I/O stack.
