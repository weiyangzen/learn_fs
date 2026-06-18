# File Research: sources/os/plan9/plan9/sys/src/cmd/awk/awkgram.c

Generated yacc parser for the Plan 9 awk grammar, from `/sys/src/cmd/awk/awkgram.y`.

Key behavior:
- Defines parser semantic type `YYSTYPE` carrying `Node*`, `Cell*`, `int`, or `char*`.
- Defines awk grammar tokens from `PROGRAM` through `LASTTOKEN`, including statements, regex tokens, operators, builtins, variables, literals, getline, function calls, and control-flow tokens.
- Maintains parser state:
  - `beginloc`
  - `endloc`
  - `infunc`
  - `inloop`
  - `curfname`
  - `arglist`
- Provides helpers:
  - `setfname()` rejects redefining arrays/functions as functions.
  - `constnode()` detects constant parse nodes.
  - `strnode()` extracts string value.
  - `notnull()` converts expressions to explicit non-null tests where needed.
  - `checkdup()` rejects duplicate function arguments.
  - `yywrap()` returns EOF.
- Contains yacc tables:
  - `yyexca`, `yyact`, `yypact`, `yypgo`, `yyr1`, `yyr2`, `yychk`, `yydef`, token maps.
- Implements Plan 9 yacc runtime parser `yyparse()` with stack depth 150, error recovery, debug hooks, and token translation through `yylex1()`.

Semantic actions:
- Builds top-level program node from begin, pattern/action, and end lists.
- Tracks loop nesting for `for`, `while`, and `do`; rejects `break`/`continue` outside loops.
- Tracks function nesting; rejects `next`/`nextfile` inside functions.
- Builds parse tree nodes with `stat*`, `op*`, `linkum`, `pa2stat`, `exptostat`, `celltonode`, `rectonode`, `makearr`, and `itonp`.
- Compiles constant regex operands immediately through `makedfa`/`compre`.
- Handles safe-mode restrictions for command pipes, `getline` from commands, and redirected/pipe print forms.
- Builds AST for awk expressions, ternary, boolean operators, match/notmatch, `in`, concatenation, arithmetic, assignment forms, increments/decrements, field indirection, arrays, function calls, builtins, `split`, `substr`, `sub`, `gsub`, `index`, `match`, and `getline`.

Important details:
- This is generated code and should normally be regenerated from `awkgram.y`, not hand-edited.
- Uses token values starting at Plan 9 yacc private range `57346`.
- Filesystem relevance is indirect: awk’s parser supports file/pipe-oriented language constructs, but this file is parser implementation, not filesystem code.
