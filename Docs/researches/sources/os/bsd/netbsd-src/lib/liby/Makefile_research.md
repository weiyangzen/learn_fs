# File Research: sources/os/bsd/netbsd-src/lib/liby/Makefile

## Summary
Builds the traditional yacc support library `liby`.

## Main Responsibilities
- Sets `NOPIC`.
- Defines `LIB=y`.
- Builds `main.c` and `yyerror.c`.
- Includes NetBSD `bsd.lib.mk`.

## Integration Notes
This produces fallback `main()` and `yyerror()` routines for yacc-generated programs that link against `-ly`.
