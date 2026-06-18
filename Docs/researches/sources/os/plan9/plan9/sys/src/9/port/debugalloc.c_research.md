# File Research: sources/os/plan9/plan9/sys/src/9/port/debugalloc.c

This file provides an alternate/debugging pool allocator implementation.

Key responsibilities:
- Defines `Pool` internals with arena chains, boundary headers, free-tree organization, and allocation counters.
- `poolalloc` finds exact or best-fit free blocks, splits blocks, allocates new arenas with `xalloc`, and optionally compacts.
- `poolfree` coalesces adjacent free blocks and reinserts them into the free tree.
- Implements `malloc`, `smalloc`, `mallocz`, `free`, `realloc`, `msize`, and `calloc` on top of the debug pool.
- Tracks allocation call sites for small blocks through the `pcx` table.
- Supports pool compaction through a caller-provided move callback.

Filesystem/storage relevance:
- Alternative allocator for diagnosing memory behavior in kernel subsystems, including VFS and storage drivers.
- Helps detect allocation pressure and fragmentation.
