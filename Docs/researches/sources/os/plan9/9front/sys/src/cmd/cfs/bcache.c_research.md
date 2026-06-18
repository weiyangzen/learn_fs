# File Research: sources/os/plan9/9front/sys/src/cmd/cfs/bcache.c

Fixed-size block cache for the caching filesystem.

Key behavior:
- `bcinit` initializes block size, disk fd, LRU list, and allocates data buffers for `Nbcache` entries.
- `bcfind` locates an existing cached block or chooses the least-recently-used entry, writing it first if dirty.
- `bcalloc` assigns a cache entry to a block without reading from disk.
- `bcread` reads a block into cache when missing or stale.
- `bcmark` marks a block dirty and appends it to the ordered dirty list; if already dirty, forces writeback.
- `bcwrite` writes dirty blocks in order through a requested block.
- `bcsync` flushes all dirty blocks.
- `bread`/`bwrite` perform positional full-block disk I/O.

Dependencies:
- Includes `cformat.h`, `lru.h`, and `bcache.h`.
- Calls `error`/`warning` supplied by the main program.

Research notes:
- Dirty ordering is explicit and important for on-disk consistency.
