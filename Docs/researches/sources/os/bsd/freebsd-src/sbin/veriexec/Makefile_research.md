# File Research: sources/os/bsd/freebsd-src/sbin/veriexec/Makefile

## Purpose
Builds the `veriexec` manifest-loading and control utility.

## Main Elements
- Sets `PROG=veriexec`, `MAN=veriexec.8`.
- Builds `veriexec.c`, `manifest_parser.y`, and `manifest_lexer.l`.
- Links `veriexec`, `secureboot`, and `bearssl`.
- Leaves `NO_SHARED` empty.
- Adds current directory include path and parser/lexer warning suppressions.

## Dependencies And Integration
Requires libveriexec, libsecureboot, BearSSL, yacc, and lex integration through FreeBSD make rules.

## Risk Notes
Parser and lexer warning suppressions are target-specific; generated code behavior depends on yacc/lex output.
