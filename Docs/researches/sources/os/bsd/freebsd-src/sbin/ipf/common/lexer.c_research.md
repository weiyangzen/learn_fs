# File Research: sources/os/bsd/freebsd-src/sbin/ipf/common/lexer.c

## Purpose
Hand-written lexer used by IPFilter yacc parsers.

## Main Elements
- `yylex()` tokenizes comments, whitespace, continuations, variable references, quoted strings, numbers, hex numbers, comparison/range operators, punctuation, identifiers, and IPv6 addresses.
- Supports dictionary-driven keyword lookup with `yysettab`, `yysetdict`, `yysetfixeddict`, and `yyresetdict`.
- Expands variables via `get_variable()`.
- Tracks parser context through globals such as `yyexpectaddr`, `yybreakondot`, and `yyvarnext`.
- Converts token text into `yylval` for numbers, hex values, strings, and IPv6 addresses.
- `yyerror()` reports the current token and line before exiting.
- Optional `TEST_LEXER` main prints token streams.

## Dependencies And Integration
The `ipf` Makefile transforms this source by renaming `yy` symbols to `ipf_yy` and switching generated header names. It depends on `ipf.h`, `lexer.h`, and yacc token definitions.

## Risk Notes
Global mutable lexer state and fixed-size token buffers make parser behavior sensitive to reset paths. `YYBUFSIZ` protects against overly long tokens by returning `TOOLONG`.
