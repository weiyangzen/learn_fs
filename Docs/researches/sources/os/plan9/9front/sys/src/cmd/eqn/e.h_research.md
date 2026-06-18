# File Research: sources/os/plan9/9front/sys/src/cmd/eqn/e.h

This header is the shared interface for the eqn implementation. It defines lexical character classes, font constants, device constants, symbol-table structures, input-source structures, argument frames, font stack entries, global state declarations, and function prototypes.

Key contents:
- Character classes used for spacing: `OTHER`, `OLET`, `ILET`, `DIG`, `LPAR`, `RPAR`, etc.
- Font constants: roman, italic, bold, bold italic.
- Device types: CAT, 202, APS, PostScript.
- `tbl` for keyword/reserved/definition/tuning hash tables.
- `Infile`, `Src`, `Arg`, and `Font` for input handling, macro arguments, and font stack.
- Global layout arrays for heights, baselines, fonts, classes, and string-register allocation.
- Prototypes for lexer/input helpers and every equation layout operator.

Important implementation notes:
- Error-reporting macros build `errbuf` and call `error` or `yyerror`.
- Many functions are old-style C declarations, matching the vintage code style.
