# File Research: sources/os/plan9/9front/sys/src/cmd/grep/grep.y

Yacc grammar and lexer for grep regular expressions. It supports alternation, concatenation, `*`, `+`, `?`, grouping, anchors, dot, character classes, escaped literals, and newline-separated multiple patterns.

The completed regex is wrapped so it can match anywhere in a line and terminate at line end. The lexer supports literal mode after leading `*`, reads class bodies into the shared string buffer, folds escapes, and reports syntax errors with pattern/file context.
