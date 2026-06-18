# File Research: sources/os/plan9/9front/sys/src/cmd/rc/syn.y

Yacc grammar for `rc`. Defines command syntax, precedence, compound commands, assignments, redirections, pipelines, conditionals, loops, functions, subshells, backquotes, variable expansion, quoting, concatenation, and word lists.

On a completed line, it reads queued here-docs and compiles the parse tree. Grammar actions build tree nodes through `tree1/tree2/tree3`, attach redirections with `mung*`, and propagate glob markers.

It distinguishes `for(i)` from `for(i in )` with an explicit empty `PAREN` node.
