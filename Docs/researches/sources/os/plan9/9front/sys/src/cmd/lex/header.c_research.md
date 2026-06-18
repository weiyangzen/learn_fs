# File Research: sources/os/plan9/9front/sys/src/cmd/lex/header.c

This file emits the generated C scanner prologue, scanner switch wrapper, tail, and generation statistics for Plan 9 `lex`.

Key functions:
- `phead1()` writes typedefs, includes, lexer macros, global declarations, scanner structs, and either Plan 9 `read`/`write`-based `input`/`output` or stdio macros.
- `phead2()` writes the `yylook()` loop and action switch header.
- `ptail()` emits switch defaults and closes `yylex`.
- `statistics()` reports parse-tree, position, state, transition, packed-class, packed-transition, and output-slot usage.

It is output-generation support for `lmain.c`/`parser.y` and depends on many global counters from `ldefs.h`.
