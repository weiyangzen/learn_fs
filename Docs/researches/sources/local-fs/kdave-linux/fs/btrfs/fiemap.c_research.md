# File Research: sources/local-fs/kdave-linux/fs/btrfs/fiemap.c

This file implements Btrfs `FIEMAP` reporting. It walks file extent items from the subvolume tree, supplements holes/prealloc ranges with delalloc state from the inode IO tree, checks sharing through backrefs, and emits merged fiemap extents to userspace.

Major responsibilities:
- Buffers fiemap output in `struct fiemap_cache` so adjacent compatible extents can be merged and so writes to a userspace fiemap buffer do not occur while holding Btrfs extent locks or cloned btree paths.
- Searches file extent items with `fiemap_search_slot()`, using cloned leaves to avoid long locks and lockdep problems while checking shared extents.
- Iterates cloned leaves with `fiemap_next_leaf_item()` while preserving leaf start offsets needed by subpage extent-buffer access.
- Processes implicit holes, explicit hole items, and prealloc extents through `fiemap_process_hole()`, reporting delalloc subranges as `FIEMAP_EXTENT_DELALLOC | FIEMAP_EXTENT_UNKNOWN` and unwritten prealloc gaps as `FIEMAP_EXTENT_UNWRITTEN`.
- Finds the last real extent end with `fiemap_find_last_extent_offset()` so the final emitted extent can receive `FIEMAP_EXTENT_LAST` when appropriate.
- Handles `FIEMAP_FLAG_SYNC` by waiting for ordered ranges before and after taking the inode shared lock, covering compression writeback that may require an extra wait.

Key data flows:
- `btrfs_fiemap()` runs `fiemap_prep()`, optionally waits ordered ranges, takes `BTRFS_ILOCK_SHARED`, optionally waits again, then calls `extent_fiemap()`.
- `extent_fiemap()` rounds the requested range to sectorsize, locks the inode IO-tree range, finds the last extent, positions a btree path, walks file extent items, emits holes/delalloc/prealloc/inline/regular/compressed extents, unlocks, flushes cached output, and emits the final cached extent.
- If the intermediary cache fills, `emit_fiemap_extent()` returns `BTRFS_FIEMAP_FLUSH_CACHE`; `extent_fiemap()` unlocks, releases the path, flushes entries, advances `start` to `next_search_offset`, and restarts the search.
- Regular and prealloc extents call `btrfs_is_data_extent_shared()` when userspace requested actual mappings, adding `FIEMAP_EXTENT_SHARED` if backrefs show sharing.

Concurrency and correctness:
- The inode IO-tree range is locked while correlating file extent items with delalloc state, preventing races with delalloc flushing and ordered extent completion.
- Cloned leaves avoid holding live btree leaves during expensive sharing checks and while userspace output could fault back into the same file.
- The cache logic trims or discards overlapping previously cached extents when concurrent ordered extent completion causes the next btree search to observe newer split file extent items.
- The output path tracks `fi_extents_max` itself because entries are buffered before reaching `fiemap_fill_next_extent()`.

Important invariants:
- Inline extents are reported as data inline and not aligned with physical address zero.
- Compressed extents are reported with `FIEMAP_EXTENT_ENCODED`; their physical contiguity is not merged as if logical length matched physical length.
- Delalloc is only searched up to i_size, while prealloc may extend beyond i_size.
- Final `FIEMAP_EXTENT_LAST` depends on the last non-hole file extent and absence of later delalloc.
