# File Research: sources/os/plan9/plan9/sys/src/cmd/cfs/inode.c

This file manages cached inode records and qid-to-inode mapping for `cfs`.

Key behavior:
- `iinit()` initializes disk state, reads inode metadata, creates the in-memory qid map, initializes inode LRU lists, and loads active inodes.
- `iformat()` formats allocation blocks and inode blocks, then reinitializes the cache.
- `ialloc()` assigns an inode cache buffer, evicting old buffer mapping state as needed.
- `iget()` finds an inode by qid path, updates stale qid versions by dropping cached data, or creates/reuses an LRU inode entry.
- `iread()` loads an inode from disk into memory and validates inode-block magic/count.
- `iwrite()` writes an inode back to its containing inode block.
- `iupdate()` forgets old data for a qid version change while preserving update ordering.
- `iremove()` marks an inode unused, frees its data pages, and drops it from LRU state.
- `iinc()` increments cached qid version after successful local cache writes.

Important details:
- Qid map lookup is linear over the configured inode count.
- New cache entries start with maximum length until server stat/read data narrows it.
- Ordering of inode writes before freeing old data is called out as important.
- Stats counters track inserts, updates, and deletes.

Filesystem relevance:
- Direct. This is the inode/index layer for `cfs`’s persistent cache.
