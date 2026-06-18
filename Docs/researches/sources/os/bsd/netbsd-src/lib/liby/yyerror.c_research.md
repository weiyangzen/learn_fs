# File Research: sources/os/bsd/netbsd-src/lib/liby/yyerror.c

## Summary
Provides the default yacc `yyerror()` routine.

## Main Responsibilities
- Assert the error message is non-null.
- Print the message to `stderr` followed by newline.
- Return `0`.

## Key Interfaces
- `yyerror(char *msg)`.

## Risks
No location, parser state, or program name context is included. It is only a minimal fallback.
