# File Research: sources/os/plan9/9front/sys/src/cmd/5e/util.c

This file provides fatal allocation wrappers for `5e`.

Functions:
- `emalloc(size)` calls `malloc`, `sysfatal()`s on failure, and records malloc tag.
- `emallocz(size)` allocates with `emalloc`, zeroes the block, and records tag.
- `erealloc(old, size)` calls `realloc`, `sysfatal()`s on failure, and records realloc tag.

Dependencies and interactions:
- Used throughout `5e` for all dynamic runtime structures.

Research relevance:
- Small utility layer but central to emulator memory allocation assumptions.

Risk notes:
- Allocation failure terminates the emulator.
- `erealloc()` does not preserve old pointer on failure because it exits immediately.
