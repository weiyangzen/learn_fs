# File Research: sources/os/plan9/9front/sys/src/cmd/awk/awkgram.y

Defines the yacc grammar for awk programs.

Key responsibilities:
- Declares awk tokens, semantic types, precedence, and grammar productions.
- Builds parse-tree nodes for programs, BEGIN/END blocks, pattern-action statements, functions, loops, conditionals, print/printf, getline, array tests, assignments, arithmetic, regex matches, split/sub/gsub, and builtins.
- Enforces safety restrictions for command pipes/redirections when `safe` is enabled.
- Tracks function and loop context to reject illegal nested functions, returns, break/continue, next/nextfile.
- Converts constant regex/string expressions into compiled regex nodes where possible.
- Defines helper functions `setfname`, `constnode`, `strnode`, `notnull`, and `checkdup`.

Important interfaces:
- Produces `yyparse` and token constants used by the rest of awk.
- Uses parse helpers from `parse.c`, regex compiler `compre`, and symbol/cell APIs.
- Updates globals `beginloc`, `endloc`, `winner`, `infunc`, `inloop`, `curfname`, and `arglist`.

Notes:
- `notnull` wraps non-boolean expressions as `expr != nullnode`.
- Function argument duplicate detection is performed during grammar reduction.
