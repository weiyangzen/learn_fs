# File Research: sources/os/plan9/9front/sys/src/cmd/upas/bayes/regcomp.c

This is a local copy/adaptation of Plan 9 `libregexp`'s regular expression compiler for the upas Bayesian filter code. It compiles a regexp string into a `Reprog` instruction program made of `Reinst` nodes and `Reclass` character classes.

Key behavior:
- Implements a stack-based regexp parser with implicit concatenation and operator precedence for grouping, alternation, concatenation, `*`, `+`, and `?`.
- Lexes UTF runes, backslash quoting, anchors, `.`, and bracket classes.
- Character classes are parsed into sorted/merged rune spans; negated classes automatically include newline as excluded from matching.
- `regcomp1` allocates a generously sized `Reprog`, builds the instruction graph, appends `END`, detects unmatched parentheses, and compacts the allocation through `optimize`.
- Exports `regcomp`, `regcomplit`, and `regcompnl`; `regcompnl` makes `.` include newline.

Integration and risks:
- Relies on `regexp.h` for public structs and `regcomp.h` for internal instruction constants.
- Error handling calls external `regerror` and then `longjmp`s through `regkaboom`.
- The file comment notes the copied implementation “leaks extra classes when it runs out”; `newclass` allocates an extra 128-class block when the embedded `Reprog.class` pool is exhausted, but `optimize` only relocates classes tied into instructions. This is acceptable for the command’s short-lived compilation path but important for long-lived use.
