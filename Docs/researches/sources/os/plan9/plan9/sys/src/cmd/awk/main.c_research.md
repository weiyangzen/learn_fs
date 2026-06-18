# File Research: sources/os/plan9/plan9/sys/src/cmd/awk/main.c

Awk program entry point.

Parses options:

- `-safe`
- `-f programfile`
- `-F fieldsep`
- `-v var=value`
- legacy `-m[rf]`
- `-d`
- `-V`

Initializes the symbol table, records, built-in variables, `ARGV`, optionally `ENVIRON`, then runs `yyparse()`. If parsing succeeds, it sets `compile_time = 0` and calls `run(winner)`.

Also implements `pgetc()` for reading multiple `-f` source files and `cursource()` for error reporting.
