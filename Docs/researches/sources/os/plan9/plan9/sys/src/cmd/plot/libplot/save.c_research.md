# File Research: sources/os/plan9/plan9/sys/src/cmd/plot/libplot/save.c

Saves the active plotting environment.

Key responsibilities:
- Copies `e1` into the next environment slot.
- Advances `e1`.

Notable risks:
- The environment array has finite size in `subr.c`, but `save()` performs no overflow check.
