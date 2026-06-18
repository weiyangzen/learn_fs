# File Research: sources/os/plan9/9front/sys/src/cmd/lex/lmain.c

This is the main driver for Plan 9 `lex`. It parses options, opens input/output, initializes global storage, runs the yacc parser, generates follow sets and DFA transitions, lays out output tables, appends the lex runtime driver template, and prints optional statistics.

Key phases:
- Options include output to stdout (`-t`/`-T`), reporting (`-v`/`-n`), and Plan 9 output mode (`-9`).
- `get1core()`, `get2core()`, and `get3core()` allocate successive work arrays for definitions, parse trees, DFA construction, and final table packing.
- `free1core()`, `free2core()`, and debug-only `free3core()` release phase-specific storage.
- Main flow: read first char, initialize `INITIAL`, `yyparse()`, emit scanner tail, `mkmatch()`, `cfoll()`, `cgoto()`, `layout()`, append `/sys/lib/lex/ncform`.

The implementation is classic batch compiler structure with explicit memory phase management.
