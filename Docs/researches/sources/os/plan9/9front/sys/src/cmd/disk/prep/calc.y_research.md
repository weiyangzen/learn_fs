# File Research: sources/os/plan9/9front/sys/src/cmd/disk/prep/calc.y

Yacc grammar and evaluator for partition-size expressions in `disk/prep`.

Key behavior:
- Parses numbers, `.`, `$`, parentheses, addition, subtraction, multiplication, division, unary minus, and postfix `%`.
- Numeric suffixes `k`, `m`, `g`, `t` scale byte quantities and convert them to sectors using `unit`.
- `.` evaluates to current position, `$` to end, and `%` evaluates a percentage of total size.
- `parseexpr` sets parser context, runs `yyparse`, evaluates the expression tree, and returns an error string or nil.

Notable dependencies:
- `disk.h`, `edit.h`, and `emalloc` from the surrounding prep program.

Research notes:
- Uses `setjmp`/`longjmp` for parse/evaluation errors such as division by zero.
- The `#ifdef TEST` main appears stale: its call to `parseexpr` does not match the current parameter list.
