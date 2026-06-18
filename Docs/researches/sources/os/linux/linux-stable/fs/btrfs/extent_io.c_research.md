# File Research: sources/os/linux/linux-stable/fs/btrfs/extent_io.c

## Purpose

`extent_io.c` is Btrfs' main extent I/O implementation for page-cache data I/O and btree metadata extent-buffer I/O. It connects inode extent maps, delalloc state, ordered extents, folio/subpage state, bio construction, metadata buffer lifetime, and extent-buffer byte access helpers.

## Main Responsibilities

- Data read path:
  - `btrfs_read_folio()` and `btrfs_readahead()` lock stable file ranges with `lock_extents_for_read()`, call `btrfs_do_readpage()`, and submit accumulated bios.
  - `btrfs_do_readpage()` resolves extent maps, handles holes, inline extents, compressed extents, fsverity verification, EOF zeroing, and readahead expansion.
  - `end_bbio_data_read()` updates folio uptodate state, zeroes post-i_size ranges, verifies fsverity data, and unlocks folios or subpage ranges.

- Data writeback path:
  - `btrfs_writepages()` drives `extent_write_cache_pages()` with a `btrfs_bio_ctrl`.
  - `extent_writepage()` handles EOF invalidation/zeroing, delalloc conversion, COW fixup, sector submission, error propagation, and folio unlocking.
  - `writepage_delalloc()` finds and locks delalloc ranges, runs `btrfs_run_delalloc_range()`, handles async compression/inline paths, and maintains subpage submit bitmaps.
  - `extent_write_locked_range()` submits already-locked ranges, used when delalloc has already produced ordered extents.

- Bio assembly:
  - `struct btrfs_bio_ctrl` tracks the current bio, next file offset, compression type, ordered-extent boundary, checksum generation optimization, writeback control, submit bitmap, readahead context, and last compressed extent-map start.
  - `submit_extent_folio()` merges compatible folio ranges into bios, splits at ordered extent boundaries and bio limits, and tracks max read extent generation.
  - `submit_one_bio()` chooses normal vs compressed read submission and applies checksum commit-root lookup optimization for old data extents.

- Metadata extent-buffer I/O:
  - `btree_writepages()` scans `fs_info->buffer_tree` xarray marks, tags dirty buffers, handles zoned metadata write-pointer constraints, and writes dirty extent buffers.
  - `lock_extent_buffer_for_io()`, `write_one_eb()`, `prepare_eb_write()`, and `end_bbio_meta_write()` coordinate metadata dirty/writeback state, folio writeback state, cgroup accounting, and error reporting.
  - `read_extent_buffer_pages_nowait()` and `read_extent_buffer_pages()` submit metadata reads and validate parent checks in `end_bbio_meta_read()`.

- Extent-buffer allocation and lifetime:
  - Extent buffers are slab-allocated through `extent_buffer_cache`.
  - `alloc_extent_buffer()` creates or finds xarray-backed metadata buffers, attaches folios, handles subpage metadata state, sets lockdep class, and installs `EXTENT_BUFFER_TREE_REF`.
  - `find_extent_buffer()`, `free_extent_buffer()`, `free_extent_buffer_stale()`, `try_release_extent_buffer()`, and `try_release_subpage_extent_buffer()` manage concurrent lookup/release, stale buffers, tree references, RCU freeing, and folio private state.
  - Dummy and cloned buffers are provided by `alloc_dummy_extent_buffer()` and `btrfs_clone_extent_buffer()` for tests and safe leaf snapshots.

- Extent-buffer content access:
  - `read_extent_buffer()`, `write_extent_buffer()`, `memzero_extent_buffer()`, `copy_extent_buffer*()`, `memcmp_extent_buffer()`, `memcpy_extent_buffer()`, and `memmove_extent_buffer()` abstract byte operations across one or multiple folios.
  - Bitmap helpers operate byte-wise to preserve little-endian on-disk bitmap layout and tolerate page-straddling bitmap items.

## Important Concurrency and Correctness Points

- Read paths lock inode extent-state ranges to stabilize extent maps against ordered extent completion. `can_skip_ordered_extent()` avoids deadlock by skipping ordered extents whose folios are locked and already dirty/uptodate.
- Delalloc writeback is tightly coupled to folio locks, extent-state bits, ordered extents, and subpage bitmaps; error paths explicitly finish ordered I/O when no bio will do it.
- Metadata buffers use xarray marks as dirty/writeback tags instead of normal page-cache traversal. Extent-buffer references include a special xarray tree reference tracked by `EXTENT_BUFFER_TREE_REF`.
- Subpage support is pervasive. Folio private data can represent either data or metadata subpage state, and release paths must not detach private state while other extent buffers in the same folio still exist.
- Zoned filesystems add ordering constraints: metadata writeback is serialized with zoned metadata locks, and clearing dirty buffers may mark `EXTENT_BUFFER_ZONED_ZEROOUT` instead of dropping dirty state.

## Dependencies and Callers

This file depends heavily on `extent-io-tree`, `extent_map`, ordered extents, compression, bio submission, file items, fsverity, subpage helpers, transaction state, and zoned block-group logic. Its exported functions are used by Btrfs address-space operations, btree block reads, transaction commit/writeback, fsync/logging paths, and folio release/invalidation hooks.
