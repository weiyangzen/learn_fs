# File Research: sources/os/linux/linux/fs/btrfs/fiemap.c

Read completely: 928 lines.

This file implements Btrfs FIEMAP support, translating Btrfs file extent items, holes, prealloc extents, delalloc ranges, compression state, and shared-extent checks into user-visible `fiemap` records.

Core responsibilities:
- Provides `btrfs_fiemap()` as the filesystem entry point after `fiemap_prep()`.
- Implements `extent_fiemap()` to scan file extent items over the requested range and emit FIEMAP records.
- Uses a `fiemap_cache` to merge adjacent compatible records and to buffer entries before copying to the user fiemap buffer.
- Handles regular extents, compressed extents, inline extents, explicit holes, implicit holes from `NO_HOLES`, prealloc extents, delalloc ranges, shared extents, and final extent marking.

FIEMAP cache behavior:
- `emit_fiemap_extent()` caches one pending extent, merges it with the next when logical/physical offsets and flags allow, and flushes older records into an intermediary page-sized array.
- The intermediary cache avoids deadlock when the fiemap buffer is mmaped from the same file, because direct writes to the user buffer could trigger `btrfs_page_mkwrite()` while the file range is locked.
- Handles races where ordered extents complete after the code unlocks and restarts, including overlapping newly found file extent items.
- Uses `BTRFS_FIEMAP_FLUSH_CACHE` as an internal restart signal when the intermediary cache is full.
- `emit_last_fiemap_cache()` emits the final cached extent and normalizes the max-entries return.

Tree search and cloned leaves:
- `fiemap_search_slot()` finds the first extent item at or before the requested file offset.
- It clones the leaf with `btrfs_clone_extent_buffer()` and releases the real path to avoid holding btree locks while doing expensive shared-extent backref checks.
- `fiemap_next_leaf_item()` advances through cloned leaves and reuses the clone across leaf transitions when possible.
- Cloned extent buffers are marked unmapped and preserve `start` before copying so subpage offset calculations stay correct.

Hole/prealloc processing:
- `fiemap_process_hole()` searches the inode io-tree for delalloc inside a hole or prealloc range.
- For holes, it emits delalloc extents as `FIEMAP_EXTENT_DELALLOC | FIEMAP_EXTENT_UNKNOWN`.
- For prealloc extents, it emits unwritten prealloc parts and delalloc parts separately.
- Shared-state checks for prealloc extents are done once per extent when output capacity is nonzero.

Extent scanning:
- `fiemap_find_last_extent_offset()` finds the logical end of the last real file extent, skipping explicit hole items, so the final emitted record can get `FIEMAP_EXTENT_LAST`.
- `extent_fiemap()` rounds the requested range to sectorsize, locks the inode io-tree range, searches the subvolume tree, processes implicit gaps, decodes file extent item type/compression/generation/disk bytenr, and emits records.
- Regular extents are checked with `btrfs_is_data_extent_shared()` when user output is requested.
- Compressed extents get `FIEMAP_EXTENT_ENCODED`.
- Inline extents get `FIEMAP_EXTENT_DATA_INLINE | FIEMAP_EXTENT_NOT_ALIGNED`.
- The function responds to fatal signals with `-EINTR` and periodically reschedules.

SYNC behavior:
- `btrfs_fiemap()` calls `fiemap_prep()`.
- With `FIEMAP_FLAG_SYNC`, it waits for ordered ranges before taking the inode lock and again after taking the shared inode lock.
- The second wait covers writes that may have started between initial prep/wait and inode locking.
- The extra ordered wait is especially important for compression, where initial writeback can only kick off async compression before real ordered writeback begins.

Important interactions:
- Uses subvolume tree file extent items as the primary source of extent layout.
- Uses the inode io-tree to detect delalloc inside holes/prealloc extents.
- Uses backref share-check context to report `FIEMAP_EXTENT_SHARED`.
- Uses cloned `extent_buffer` helpers from `extent_io.c`.
- Coordinates with ordered extents, compression, file locking, path release, and user fiemap buffer filling.

Risk and correctness notes:
- FIEMAP must avoid reporting overlapping extents while ordered extents may complete during restarts; cache trimming/discard logic handles those races.
- Holding the io-tree lock while emitting directly to a user buffer can deadlock if the buffer maps the same file, so this file buffers records and releases paths before final emission.
- Shared extent detection can be expensive, motivating cloned leaves and lock release.
- Delalloc detection is only meaningful up to `i_size`; preallocation may extend beyond `i_size`.
