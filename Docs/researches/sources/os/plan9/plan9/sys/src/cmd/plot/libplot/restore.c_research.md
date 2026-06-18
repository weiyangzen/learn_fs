# File Research: sources/os/plan9/plan9/sys/src/cmd/plot/libplot/restore.c

Restores the previous plotting environment.

Key responsibilities:
- Decrements `e1`.
- Restores current point by calling `move()` with the restored environment’s saved coordinates.

Notable risks:
- No underflow guard; unmatched `restore()` can move before the environment stack.
