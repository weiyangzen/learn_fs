# File Research: sources/os/bsd/freebsd-src/sbin/veriexec/veriexec.h

## Purpose
Shared declarations for Veriexec source, lexer, and parser.

## Main Elements
- Includes Veriexec ioctl definitions.
- Declares shared globals: `dev_fd`, `parser_version`, `ForceFlags`, `Verbose`, `VeriexecVersion`, and `Cdir`.
- Defines `VERBOSE(n, x)` debug-print macro.
- Declares `manifest_open()`, `manifest_parser_init()`, `yyparse()`, and `yyin`.

## Dependencies And Integration
Included by the lexer, parser, and main program.

## Risk Notes
Parser/lexer behavior depends on shared mutable globals initialized by `veriexec.c`.
