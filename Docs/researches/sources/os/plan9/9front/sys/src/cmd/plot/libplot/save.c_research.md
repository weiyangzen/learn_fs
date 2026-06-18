# File Research: sources/os/plan9/9front/sys/src/cmd/plot/libplot/save.c

This primitive saves the current plotting environment.

Key behavior:
- Copies `e1` to `e1 + 1` with `sscpy()`.
- Advances `e1` to the saved environment slot.

Filesystem relevance:
- None.
