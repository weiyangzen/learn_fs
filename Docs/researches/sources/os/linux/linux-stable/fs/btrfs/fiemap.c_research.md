# File Research: sources/os/linux/linux-stable/fs/btrfs/fiemap.c

## Purpose

`fiemap.c` implements Btrfs' `FIEMAP` ioctl support. It reports logical-to-physical file extent mappings while handling Btrfs-specific realities: holes, prealloc extents, inline data, compression, delalloc, shared extents, ordered extent completion, and concurrent tree changes.

## Fiemap Cache

`struct fiemap_cache` buffers and merges fiemap entries before copying them to the user-provided fiemap buffer.

It serves two purposes:

- Merge contiguous logical and physical extents with identical flags.
- Avoid deadlocks when the fiemap output buffer is mmaped to the same file, by buffering entries while the file range and tree path are locked, then flushing after unlocking.

`emit_fiemap_extent()` is the central merge/cache function. It handles overlapping or stale ranges caused by ordered extents completing while the path/range had to be unlocked. When the intermediate cache is full, it returns `BTRFS_FIEMAP_FLUSH_CACHE`, causing the main scan to unlock, flush, and restart from `next_search_offset`.

## Tree Scanning

- `fiemap_search_slot()` finds the first file extent item at or before the requested offset.
- It clones the current leaf with `btrfs_clone_extent_buffer()` before long processing so fiemap does not hold a real btree leaf locked during expensive shared-extent checks.
- `fiemap_next_leaf_item()` advances within the cloned leaf or moves to the next leaf, recloning as needed.
- `fiemap_find_last_extent_offset()` finds the last non-hole file extent end so the final emitted extent can be tagged `FIEMAP_EXTENT_LAST` when appropriate.

## Hole, Prealloc, and Delalloc Handling

`fiemap_process_hole()` processes implicit holes, explicit hole file extent items, and prealloc extents.

- For holes, it searches the inode io tree for delalloc ranges and emits them as `FIEMAP_EXTENT_DELALLOC | FIEMAP_EXTENT_UNKNOWN`.
- For prealloc extents, it emits unwritten physical ranges with `FIEMAP_EXTENT_UNWRITTEN`, splitting around delalloc ranges.
- Shared state for prealloc extents is checked through `btrfs_is_data_extent_shared()` only when output extents are requested.
- Searches are capped at `i_size` for delalloc because no delalloc exists beyond EOF.

## Main Algorithm

`extent_fiemap()`:

1. Allocates the intermediate cache, backref share-check context, and btree path.
2. Rounds the requested range to sectorsize boundaries.
3. Locks the corresponding inode io-tree range to stabilize delalloc and ordered extent state.
4. Finds the last extent and the first relevant file extent item.
5. Walks file extent items, handling:
   - implicit holes before the next file extent item,
   - inline extents with `FIEMAP_EXTENT_DATA_INLINE | FIEMAP_EXTENT_NOT_ALIGNED`,
   - prealloc extents through `fiemap_process_hole()`,
   - explicit holes through `fiemap_process_hole()`,
   - regular extents with optional `FIEMAP_EXTENT_ENCODED` for compression and `FIEMAP_EXTENT_SHARED` for shared extents.
6. Checks trailing EOF delalloc or holes.
7. Tags the final cached extent as `FIEMAP_EXTENT_LAST` when no later real or delalloc extent exists.
8. Unlocks, flushes cached entries, emits the final cached entry, and frees resources.

## Public Entry Point

`btrfs_fiemap()` prepares the request with `fiemap_prep()`, optionally waits for ordered extents for `FIEMAP_FLAG_SYNC`, takes the Btrfs inode shared lock, repeats ordered waiting to close the race with new writes, calls `extent_fiemap()`, and unlocks.

## Correctness Notes

- The implementation primarily reports file extent items, consulting the io tree only for holes/prealloc ranges where delalloc may exist.
- Compression requires extra sync handling because initial writeback can only start async compression; a second ordered wait is needed for stable reporting under `FIEMAP_FLAG_SYNC`.
- Leaf cloning avoids long-held btree locks and lockdep issues during backref walking.
- Cache flush/restart logic prevents missing newly inserted extents after unlocking and avoids overlapping reports when ordered extents complete concurrently.
