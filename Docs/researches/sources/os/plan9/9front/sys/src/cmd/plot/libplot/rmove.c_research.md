# File Research: sources/os/plan9/9front/sys/src/cmd/plot/libplot/rmove.c

This primitive performs relative move.

Key behavior:
- Adds deltas to current copy position.
- Calls `move()` to update current position without drawing.

Filesystem relevance:
- None.
