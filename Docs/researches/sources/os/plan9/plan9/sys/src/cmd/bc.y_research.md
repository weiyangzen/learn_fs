# File Research: sources/os/plan9/plan9/sys/src/cmd/bc.y

Yacc grammar and translator for Plan 9 `bc`.

This is not a standalone arithmetic engine. It parses `bc` syntax and emits `dc` program text, either to stdout with `-c` or through a pipe to `/bin/dc`.

Supports:

- Assignments and compound assignments.
- `scale`, `ibase`/`base`, and `obase`.
- `print`, strings, `sqrt`, `length`, function calls, arrays, increments/decrements.
- `if`, `while`, `for`, `break`, `return`, `define`, `auto`.
- Optional standard math library via `-l`.

The implementation builds output fragments with `bundle()` over a fixed pointer workspace, uses labels like `<128>` for branches, maps functions/arrays to encoded dc registers, and reports parser errors as dc print commands.
