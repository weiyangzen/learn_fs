# File Research: sources/os/plan9/plan9/sys/src/cmd/rc/fns.h

Cross-file function prototype hub for rc.

It declares:
- Plan 9/Unix adapter calls (`Read`, `Write`, `Seek`, `Execute`, `Waitfor`, `Opendir`, `Readdir`, `Trapinit`, `Updenv`, etc.).
- compiler/parser helpers (`compile`, `yyparse`, `yylex`, `yyerror`, `readhere`, `cleanhere`);
- interpreter helpers (`start`, `setvar`, `vlook`, `searchpath`, `globlist`, `dotrap`);
- formatting/matching/argument helpers (`match`, `mkargv`, `list2str`, `count`);
- wait-pid tracking helpers.

This file keeps old-style C compilation coherent across the rc modules.

Risk/notes:
- Several prototypes expose platform abstraction boundaries implemented in `plan9.c` and Unix-specific files outside this group.
