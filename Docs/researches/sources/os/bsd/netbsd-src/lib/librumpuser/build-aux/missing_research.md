# File Research: sources/os/bsd/netbsd-src/lib/librumpuser/build-aux/missing

Read completely: 215 lines.

## Purpose
Vendored Automake helper that runs optional maintainer tools and prints useful advice when those tools are missing or too old.

## Main Responsibilities
- Supports `--help`, `--version`, `--is-lightweight`, and legacy `--run`.
- Runs the requested program and exits successfully if it succeeds.
- If the program fails with status 127, reports that it is missing.
- If it fails with status 63, reports that it is probably too old.
- Leaves ordinary tool failures unchanged.
- Normalizes tool names by stripping `gnu-`, `gnu`, or `g` prefixes before selecting advice.
- Provides targeted guidance for `aclocal`, `autoconf`, `autoheader`, `autom4te`, `automake`, `bison`/`yacc`, `flex`/`lex`, `help2man`, and `makeinfo`.

## Filesystem Relevance
None beyond build maintenance. It neither implements filesystem behavior nor affects rump runtime logic.

## Dependencies
- POSIX shell, `sed`, and `printf`.
- External maintainer tools when invoked.
