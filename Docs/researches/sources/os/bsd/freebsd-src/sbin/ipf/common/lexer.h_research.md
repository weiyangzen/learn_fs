# File Research: sources/os/bsd/freebsd-src/sbin/ipf/common/lexer.h

## Purpose
Declares lexer token constants and public lexer state/functions.

## Main Elements
- Defines fallback token IDs under `NO_YACC`.
- Defines `YYBUFSIZ` as 8192.
- Declares dictionary management functions, `yylex`, `yyerror`, `yykeytostr`, and `yyresetdict`.
- Exposes `yyin`, `yylineNum`, `yyexpectaddr`, `yybreakondot`, and `yyvarnext`.

## Dependencies And Integration
Included by `lexer.c` and transformed into parser-specific lexer headers such as `ipf_l.h`.

## Risk Notes
The exposed globals are part of parser control flow; callers must reset them correctly between parse sessions.
