# File Research: sources/os/linux/linux-stable/fs/ocfs2/uptodate.c

Implements OCFS2 clustered metadata uptodate tracking. Standard buffer-head uptodate flags are insufficient in a cluster because another node may modify metadata, so this file maintains per-owner hints for which metadata blocks can be trusted locally without reread.

Key responsibilities:
- Initialize, purge, and destroy `struct ocfs2_caching_info` metadata caches.
- Store cached block numbers either in a small inline array or, after expansion, an rb-tree of `ocfs2_meta_cache_item`.
- Check whether a buffer is locally uptodate and trusted for the owner.
- Mark existing or newly allocated metadata buffers as uptodate in the owner cache.
- Remove single blocks or xattr cluster ranges from the cache.
- Provide owner, superblock, spinlock, and I/O-lock dispatch through `struct ocfs2_caching_operations`.
- Maintain the global slab `ocfs2_uptodate_cachep`.

Important behavior:
- `ocfs2_buffer_uptodate()` returns false if the buffer is not marked uptodate; returns true for journaled buffers on this node; otherwise checks the owner metadata cache.
- `ocfs2_buffer_read_ahead()` reports locked cached buffers as active readahead, assuming the caller holds the I/O semaphore.
- `ocfs2_set_buffer_uptodate()` first avoids duplicates, appends to the inline array when possible, and expands to an rb-tree when the inline capacity is exceeded.
- Expansion preallocates all required rb-tree items outside the cache spinlock and handles races where purge/removal occurred during allocation.
- `ocfs2_set_new_buffer_uptodate()` sets the buffer uptodate flag and inserts it while holding the owner I/O lock.
- `ocfs2_metadata_cache_purge()` snapshots the rb-tree root under lock, resets the cache, and frees tree items outside the lock.
- Removing from a tree erases under the cache lock, then frees the item after unlocking.

Integration points:
- Used by metadata I/O, inode/dinode reads, allocator group descriptor reads, journal access, xattr cache removal, and lock downconversion paths.
- `ocfs2_inode_init_once()` initializes inode metadata caches with inode caching operations.

Risk areas:
- The cache is a strong hint, not a pinned buffer list; callers still rely on `buffer_uptodate()` and journal state.
- Insertions are serialized by the owner I/O lock; removals/purges can race with slow allocation paths and are explicitly handled.
- Count mismatches during purge indicate cache accounting bugs.
- Not reverting tree caches back to arrays after removals is intentional.
