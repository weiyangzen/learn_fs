# File Research: sources/os/bsd/netbsd-src/lib/liby/main.c

## Summary
Provides a minimal yacc-compatible `main()` implementation.

## Main Responsibilities
- Declare external `yyparse()`.
- Ignore command-line arguments.
- Return the result of `yyparse()`.

## Key Interfaces
- `main(int argc, char *argv[])`.

## Risks
Programs linking this default entry point get no argument handling or setup; all behavior must be in the parser and lexer.
