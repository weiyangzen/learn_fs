# File Research: sources/os/plan9/9front/sys/src/cmd/rc/here.c

Handles here-document collection and substitution. `heredoc()` queues parser redirection nodes; `readhere()` consumes queued here-doc bodies after a complete parsed line.

`readhere1()` prompts as needed, tracks lexer line numbers, rejects NUL bytes, and stops when the tag line matches. `psubst()` performs `$name`, `$n`, and `$$` substitution for unquoted here-doc bodies, preserving multibyte sequences carefully.

The executor later writes bodies into temporary files in `exec.c`.
