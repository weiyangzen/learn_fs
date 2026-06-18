# File Research: sources/os/plan9/plan9/sys/src/cmd/plot/libplot/rmove.c

Relative move operation.

Key responsibilities:
- Adds deltas to current `copyx/copyy`.
- Calls `move()` with the updated absolute position.
