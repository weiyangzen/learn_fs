# File Research: sources/os/linux/linux/fs/ocfs2/uptodate.c

## Purpose

`uptodate.c` implements OCFS2's clustered metadata buffer uptodate cache. Standard `buffer_uptodate` state is only local to a node, so OCFS2 tracks which metadata blocks are known valid relative to cluster locking without pinning `buffer_head` objects.

## Cache Model

Each cache is embedded in an owner-specific `struct ocfs2_caching_info` and uses owner-provided operations for:

- Owner id logging.
- Superblock lookup.
- Non-sleeping cache lock/unlock.
- Sleeping I/O lock/unlock.

The cache stores block numbers, not buffer heads:

- Starts as an inline fixed array with `OCFS2_CACHE_INFO_MAX_ARRAY` entries.
- Expands to an RB-tree of `struct ocfs2_meta_cache_item` when the array fills.
- Does not shrink back to the inline representation.

`ocfs2_uptodate_cachep` is a slab cache for RB-tree items.

## Public Operations

- `ocfs2_metadata_cache_init()` sets operations and resets state.
- `ocfs2_metadata_cache_exit()` purges and resets the cache.
- `ocfs2_metadata_cache_purge()` clears all cached block numbers and frees tree nodes outside the cache lock.
- `ocfs2_metadata_cache_owner()` returns owner id through callbacks.
- `ocfs2_metadata_cache_get_super()` gets the backing superblock through callbacks.
- `ocfs2_metadata_cache_io_lock()` / `ocfs2_metadata_cache_io_unlock()` call owner-provided I/O serialization.
- `ocfs2_buffer_uptodate()` decides whether a buffer can be trusted.
- `ocfs2_buffer_read_ahead()` detects an in-flight readahead buffer that is already tracked in the cache.
- `ocfs2_set_buffer_uptodate()` inserts a buffer block into the cache.
- `ocfs2_set_new_buffer_uptodate()` marks a newly allocated buffer locally uptodate and inserts it under the I/O lock.
- `ocfs2_remove_from_cache()` removes one block.
- `ocfs2_remove_xattr_clusters_from_cache()` removes all blocks covered by xattr clusters.
- `init_ocfs2_uptodate_cache()` and `exit_ocfs2_uptodate_cache()` manage the slab cache.

## Trust Rules

`ocfs2_buffer_uptodate()` returns false if `buffer_uptodate(bh)` is false. If the buffer is journaled on the local node (`buffer_jbd(bh)`), it returns true because OCFS2 prevents multiple nodes from modifying the same metadata block simultaneously. Otherwise it requires the block number to be present in the OCFS2 metadata cache.

This gives a strong hint without pinning buffer heads and relies on the I/O path, DLM lock invalidation, and journal access rules to purge or trust entries correctly.

## Insert Path

`ocfs2_set_buffer_uptodate()`:

- Avoids duplicate work if `ocfs2_buffer_cached()` already finds the block.
- Uses a fast path when the cache is still inline and has capacity.
- Switches to the slow path when allocation or tree expansion is needed.

`__ocfs2_set_buffer_uptodate()`:

- Allocates the new tree item before taking the cache lock.
- If expansion is needed, allocates one tree item per existing inline-array entry.
- Rechecks whether removals made array insertion possible while allocation was in progress.
- Expands the array to an RB-tree with `ocfs2_expand_cache()` and inserts the new item.

The insertion path relies on the owner I/O lock to prevent concurrent duplicate inserts and concurrent tree expansions.

## Removal and Purge

- Inline removal uses `memmove()` to keep the array compact.
- Tree removal erases the RB node under lock and frees the item after unlocking.
- Purge saves the RB root, resets the cache under lock, then frees all copied tree nodes outside the lock.
- Purge tracks the expected count and logs if the number of freed nodes differs.

## Correctness Notes

- A true result from `ocfs2_buffer_cached()` alone does not prove the buffer is safe; callers use `ocfs2_buffer_uptodate()` so local buffer state and journal state are also considered.
- Readahead can insert buffers before I/O completion; `ocfs2_buffer_read_ahead()` handles the locked-buffer case.
- `ocfs2_set_new_buffer_uptodate()` asserts the block is not already cached, sets the normal buffer uptodate flag, and serializes insertion with the I/O lock.
- Allocation failure in the slow insert path is non-fatal and only reduces caching performance.
