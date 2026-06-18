# File Research: sources/os/plan9/plan9/sys/src/cmd/ssh2/funclen

This is an rc/awk utility that reports C function lengths.

Key behavior:
- Scans one or more C files, looking for function declarations using Plan 9/V7 brace style.
- Tracks opening and closing braces to print `linecount file:start,end function()`.
- Emits diagnostics for unclosed functions or unmatched function ends.

Important details:
- It deliberately skips preprocessor/comment-like lines, lines ending in semicolons, macro continuations, and some non-function patterns.
- It tolerates a limited set of return type spellings and identifier characters.
- It is a heuristic source-analysis helper, not a parser.

Filesystem relevance:
- Indirect: development utility in the SSH source directory, not runtime filesystem code.
