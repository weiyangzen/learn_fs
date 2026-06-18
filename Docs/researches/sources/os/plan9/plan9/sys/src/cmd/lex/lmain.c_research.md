# File Research: sources/os/plan9/plan9/sys/src/cmd/lex/lmain.c

Read fully: 296 lines, 6173 bytes. SHA-256 prefix: `ead3db77e0529ab7`.

This is the main program and storage manager for Plan 9 `lex`. It defines the generator’s global state, parses options (`-t`, `-v`, `-n`, `-9`, debug options under `DEBUG`), opens input and output, initializes the default `INITIAL` start condition, runs `yyparse()`, generates follow sets and DFA states, packs tables, appends the runtime driver from `/sys/lib/lex/ncform`, and optionally prints statistics.

Memory setup is staged:
- `get1core()` allocates definitions, start conditions, and character-class storage.
- `get2core()` allocates DFA construction arrays after parsing.
- `get3core()` allocates final packed output tables.
- matching `free*core()` routines release earlier stages.

Integration: orchestrates parser actions from `parser.y`, helper logic from `sub1.c`/`sub2.c`, and output routines from `header.c`.

Risk notes: global state and staged frees mean later phases assume earlier arrays are no longer needed except where explicitly retained.
