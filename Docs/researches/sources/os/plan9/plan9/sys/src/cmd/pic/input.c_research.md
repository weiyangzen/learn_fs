# File Research: sources/os/plan9/plan9/sys/src/cmd/pic/input.c

Implements `pic` input-source stacking, macro expansion, argument substitution, `copy`, `thru`, shell escapes, and syntax-error context reporting.

Sources can be files, strings, macros, single pushed-back chars, `thru` sentinels, or free-after-use strings. `input` and `nextchar` multiplex those sources and maintain a rolling error buffer.

Macro definitions are collected with balanced delimiters and stored in the symbol table. Macro invocation parses parenthesized args into argument frames and expands `$N` references while reading the macro body.

`copy thru` reads lines, tokenizes fields into macro arguments, expands a selected macro per line, and stops on `.PE` or an optional `until` string. `copy file` pushes a new file source.

`yyerror` prints command, file, line, nearby context, and pushes a synthetic `.PE` to recover safely.
