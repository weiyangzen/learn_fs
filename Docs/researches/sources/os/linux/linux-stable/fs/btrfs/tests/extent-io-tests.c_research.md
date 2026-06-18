# File Research: sources/os/linux/linux-stable/fs/btrfs/tests/extent-io-tests.c

## Role
Tests extent I/O tree behavior, delalloc range locking, extent-buffer bitmap helpers, clear-range search, and extent-buffer memory copy/move operations.

## Main Areas
- `process_page_range` walks contiguous folios in an inode mapping and can check lock state, unlock folios, and release references.
- `extent_flag_to_str` and `dump_extent_io_tree` provide diagnostics for failing extent-state tree tests.
- `test_find_delalloc` creates a dummy inode/root and dirty page cache pages, marks delalloc ranges in the inode I/O tree, and validates `find_lock_delalloc_range` across exact matches, overlapping searches, no-match searches, large ranges, and a range containing a page that is no longer dirty.
- `check_eb_bitmap`, `test_bitmap_set`, `test_bitmap_clear`, `__test_eb_bitmaps`, and `test_eb_bitmaps` compare extent-buffer bitmap operations against a normal kernel bitmap. They cover whole-buffer set/clear, same-byte operations, cross-byte operations, cross-page operations for multi-page nodes, and a pseudo-random bit pattern.
- `test_find_first_clear_extent_bit` validates clear-bit range discovery in an empty tree, before the first set region, between set regions, within a set region with only some requested bits set, and beyond the last known range.
- `test_eb_mem_ops` compares extent-buffer writes, memcpy, and memmove against ordinary memory for same-page and cross-page overlapping/non-overlapping cases.
- `btrfs_test_extent_io` runs delalloc, clear-bit, bitmap, and memory-operation tests in order.

## Dependencies
Uses page cache and folio APIs, Btrfs extent I/O trees, dummy roots/fs_info/inodes, extent buffers, bitmap helpers, random byte generation, and Btrfs inode state.
