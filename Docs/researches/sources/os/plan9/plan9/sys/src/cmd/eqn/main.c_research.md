# File Research: sources/os/plan9/plan9/sys/src/cmd/eqn/main.c

Main program and output driver for `eqn`.

Key behavior:
- Parses options for debug, point size, equation delimiters, font, device type, and output mode.
- Processes input files/stdin, detects `.EQ`/`.EN` display equations and inline equations, and calls `yyparse()`.
- Emits troff setup/output strings, line directives, marks, height adjustments, and final equation strings.
- Manages string-register allocation/freeing and width measurement.
- Provides point-size formatting helpers and em conversion.

Filesystem relevance:
- Opens input files specified on the command line and reads them line by line; otherwise stdin.
