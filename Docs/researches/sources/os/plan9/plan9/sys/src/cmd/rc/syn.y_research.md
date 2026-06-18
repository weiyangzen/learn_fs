# File Research: sources/os/plan9/plan9/sys/src/cmd/rc/syn.y

Yacc grammar for rc.

Defines tokens, precedence, semantic type, and grammar rules for:
- command lines and command sequencing;
- braces and parentheses;
- assignments and redirection epilogues;
- `if`, `if not`, `for`, `while`, `switch`, functions;
- simple commands, arg lists, concatenation;
- variables, quoted variables, counts, command substitution, pipefd;
- logical operators, pipes, async, subshell, match.

Actions build `tree` nodes using helpers from `tree.c`, call `heredoc()` for `<<`, and call `compile()` when a line is parsed.

Risk/notes:
- Empty `for(i in )` is represented distinctly from implicit `for(i)`.
- Switch grammar expects case commands inside the brace body and `code.c` validates that structure.
