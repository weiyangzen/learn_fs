# File Research: sources/os/plan9/9front/sys/src/cmd/cfs/inode.c

Inode cache and qid-to-cache-entry mapping for `cfs`.

Key behavior:
- `iinit` initializes disk allocator state, validates inode blocks, allocates qid map, initializes LRU lists, and builds in-core map from on-disk inodes.
- `iformat` formats disk allocation state and inode blocks, then reinitializes the inode cache.
- `ialloc` chooses an inode buffer from the LRU list and binds it to an inode number.
- `iget` finds or creates a cached inode for a server qid; stale qid versions trigger `iupdate`.
- If no unused inode map entry is available, `iget` evicts the least-recently-used cached inode with `iremove`.
- `iread` loads an inode block into memory and performs consistency checks.
- `iwrite` writes a cached inode back to its containing inode block.
- `iupdate` resets stale cached data while preserving update ordering.
- `iremove` marks an inode unused, frees associated data blocks, and demotes its map entry.
- `iinc` increments local cached qid version after successful cache update.

Dependencies:
- Uses `Disk` as the embedded base of `Icache`, block cache operations, LRU routines, and stats counters.

Research notes:
- The qid map is a linear array; comments explicitly note lookup could be faster.
- Ordering of inode writes before block frees is treated as consistency-critical.
