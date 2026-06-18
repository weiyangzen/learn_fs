# File Research: sources/os/plan9/9front/sys/src/cmd/lex/sub1.c

`sub1.c` provides lex front-end utilities, diagnostics, action copying, input buffering, parse-tree node construction, definition pushback, and debug dumps.

Key functions:
- `getl()` reads logical input lines via `gch()`.
- `error()`/`warning()` print file/line diagnostics; fatal errors may also print statistics.
- `lgate()` lazily opens `lex.yy.c` and emits the generated prologue.
- `cclinter()` computes/intersects packed character-class partitions.
- `usescape()` decodes common and octal escapes.
- `lookup()` finds definitions/start-condition names.
- `cpyact()` copies C action code while respecting braces, comments, strings, chars, semicolon termination, and `|` action reuse.
- `gch()`, `munputc()`, and `munputs()` implement source input and macro-expansion pushback across multiple files.
- `mn0()`, `mn1()`, `mn2()`, `mnp()`, and `dupl()` create/clone parse-tree nodes and nullability metadata.
- Debug-only routines print characters, strings, definitions, start conditions, and parse trees.

The file is essential glue between parser tokens, copied user code, and regex tree construction.
