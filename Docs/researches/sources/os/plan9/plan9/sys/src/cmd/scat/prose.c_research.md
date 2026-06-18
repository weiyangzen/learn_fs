# File Research: sources/os/plan9/plan9/sys/src/cmd/scat/prose.c

Expands compact astronomical object descriptions into readable prose.

Key functions:
- `append` appends text to a buffer pointer.
- `matchlen` measures prefix matches used to choose the longest abbreviation match.
- `prose` parses symbols, punctuation, numbers, star shorthand, and table-backed abbreviations into a static prose buffer.
- `prdesc` lazily builds a first-character index over `desctab`, calls `prose`, and prints the expanded description.

Behavior notes:
- `descindex` is initialized on first use.
- Unknown fragments are copied or interpreted by local punctuation/number/star rules.
- The output buffer is fixed at 512 bytes and aborts if exceeded.
