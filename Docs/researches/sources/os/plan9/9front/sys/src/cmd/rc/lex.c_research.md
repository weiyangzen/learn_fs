# File Research: sources/os/plan9/9front/sys/src/cmd/rc/lex.c

Lexer for the `rc` grammar. It recognizes words, keywords, comments, quotes, variable forms, operators, pipes, and detailed redirection syntax.

Important behavior: after a word, `(` becomes subscript syntax and adjacent word starts synthesize `^` concatenation. Globbing characters are marked with `GLOB` in token strings. Backslash-newline continues non-comment input.

`yyerror()` reports source file/line and token, consumes to newline/EOF, increments `nerror`, and sets shell status.
