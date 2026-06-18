# File Research: sources/os/plan9/plan9/sys/src/cmd/grep/grep.y

This yacc grammar parses grep regular expressions. It supports alternation, concatenation, `*`, `+`, `?`, grouping, begin/end anchors, dot, character classes, escaped characters, literal-mode handling after leading `*`, and multiple patterns separated by newlines.

The final regex is wrapped so matching can start anywhere in a line and terminate at line end. New pattern expressions are ORed into the global top regex.

The lexer reads from a string or pattern file, folds ASCII case when `-i` is active, parses bracket classes, and reports syntax errors with pattern/file context.
