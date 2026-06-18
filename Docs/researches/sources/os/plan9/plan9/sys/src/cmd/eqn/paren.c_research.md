# File Research: sources/os/plan9/plan9/sys/src/cmd/eqn/paren.c

Scalable delimiter construction for `eqn`.

Key behavior:
- Wraps a box with left/right delimiters including parentheses, brackets, braces, floor/ceiling, vertical bars, arbitrary characters, or nothing.
- Computes delimiter height from enclosed box metrics and typesetter-specific tuning.
- Builds tall delimiters from top/middle/bottom pieces using troff bracket construction.
- Adjusts baseline and optional vertical centering for unbalanced boxes.

Filesystem relevance:
- Typesetting layout only.
