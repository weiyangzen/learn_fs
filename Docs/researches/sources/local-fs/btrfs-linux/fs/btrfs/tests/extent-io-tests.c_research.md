# File Research: sources/local-fs/btrfs-linux/fs/btrfs/tests/extent-io-tests.c

This file tests extent I/O tree behavior, delalloc range finding, extent-buffer bitmap operations, clear-bit search behavior, and extent-buffer memory copy/move operations.

`test_find_delalloc()` creates a dummy root and test inode, initializes the inode's `io_tree`, creates dirty pages covering two maximum-sized file extents, and probes `find_lock_delalloc_range()`. It tests delalloc fully covering the search, delalloc overlapping the search start, no delalloc after the range, delalloc spanning from `max_bytes` to the end, and the fallback behavior when a page in the delalloc range is no longer dirty. It checks returned ranges and verifies pages in selected ranges are locked.

The file includes `extent_flag_to_str()` and `dump_extent_io_tree()` diagnostics used when delalloc/clear-bit checks fail.

`test_eb_bitmaps()` compares Linux bitmap operations against `extent_buffer_bitmap_set()`, `extent_buffer_bitmap_clear()`, and `extent_buffer_test_bit()`. It tests full set/clear, same-byte and cross-byte operations, multi-byte operations, cross-page operations when nodesize exceeds `PAGE_SIZE`, and a deterministic pseudo-random bit pattern. It runs against dummy extent buffers at offset 0 and at a sectorsize-aligned but not nodesize-aligned offset.

`test_find_first_clear_extent_bit()` validates `btrfs_find_first_clear_extent_bit()` on an empty tree, before a set range, between set ranges, while starting inside a set range, when searching for only one unset bit among mixed flags, and beyond the last known range.

`test_eb_mem_ops()` creates random memory and an extent buffer with identical contents, then compares `memcpy_extent_buffer()` and `memmove_extent_buffer()` against regular `memcpy()`/`memmove()` for same-page non-overlap, same-page overlap, and cross-page non-overlap/overlap when nodesize is larger than a page.

`btrfs_test_extent_io()` runs delalloc, first-clear-bit, bitmap, and memory-operation tests in order, stopping at the first failure.
