# File Research: sources/os/plan9/plan9/sys/src/cmd/lex/header.c

Read fully: 114 lines, 3368 bytes. SHA-256 prefix: `495c3f667c6aea23`.

This file emits the generated C scanner prelude and trailer for Plan 9 `lex`. `phead1()` writes typedefs, includes, macros, scanner globals, `yywork`/`yysvf` structures, and either Plan 9 `read`/`write` based `input()`/`output()` helpers when `-9` is active or stdio macros otherwise. `phead2()` emits the main `yylook()` switch loop. `ptail()` closes the generated `yylex()` action switch once. `statistics()` reports table usage and generation counts.

Integration: called from `parser.y` during section transitions and from `lmain.c` after parsing. It writes to global `fout`.

Risk notes: output is generated with raw `Bprint()` fragments, so correctness depends on exact ordering from parser actions.
