# File Research: sources/os/plan9/9front/sys/src/cmd/awk/main.c

Implements the Plan 9 awk command entry point.

Key responsibilities:
- Initializes floating-point control, standard `Biobuf`s, notification handler, PRNG seed, and symbol table.
- Parses options: `-safe`, `-f programfile`, `-F fieldsep`, `-v var=value`, and `-d`.
- Selects inline program text or one or more `-f` program files.
- Initializes records, built-in symbols, `ARGV`/`ARGC`, and then runs `yyparse`.
- Applies `-F` after parsing, then runs the compiled parse tree if no syntax error occurred.
- Provides `pgetc` to feed source characters to the lexer across multiple program files.
- Provides `cursource` for diagnostics.

Important interfaces:
- Calls `recinit`, `syminit`, `arginit`, `yyparse`, `run`, and `bracecheck`.
- Sets global `compile_time` to distinguish command-line, compile, and runtime phases.

Notes:
- `-F t` maps to tab as a historical awk wart.
