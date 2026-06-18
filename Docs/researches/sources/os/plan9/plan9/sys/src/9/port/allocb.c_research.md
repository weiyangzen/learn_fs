# File Research: sources/os/plan9/plan9/sys/src/9/port/allocb.c

This file implements allocation and validation for Plan 9 `Block` packet/buffer objects.

Key responsibilities:
- Computes total memory required for a `Block` plus header slack and alignment via `blocksize`.
- `mem2block` initializes a `Block` over malloced or caller-provided memory.
- `allocb` allocates normal process-context blocks and panics on exhaustion.
- `iallocb` allocates interrupt-context blocks under `conf.ialloc` accounting and returns `nil` on pressure.
- `freeb` reference-counts blocks, calls custom free callbacks when present, updates interrupt allocation accounting, poisons dead blocks, and frees memory.
- `checkb` validates block magic and pointer bounds.
- `iallocsummary` reports interrupt allocation usage.

Filesystem/storage relevance:
- `Block` is the common buffer type for network and some device I/O, including AoE packet transport and generic `devbread`/`devbwrite` wrappers.
