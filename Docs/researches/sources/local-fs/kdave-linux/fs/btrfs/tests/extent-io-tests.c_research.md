# File Research: sources/local-fs/kdave-linux/fs/btrfs/tests/extent-io-tests.c

This file tests extent I/O tree behavior, delalloc range discovery, extent-buffer bitmap helpers, clear-bit search, and extent-buffer memory copy/move operations.

`process_page_range()` walks contiguous folios in an inode mapping and can verify locked state, unlock pages, and release folios. It supports the delalloc tests by checking page-lock behavior across ranges.

`test_find_delalloc()` builds a dummy inode with dirty pages and an initialized `extent_io_tree`, then validates `find_lock_delalloc_range()` across delalloc ranges aligned with the search, overlapping the search start, outside the search, spanning large max extent ranges, and interrupted by a page that is no longer dirty.

The file includes debug helpers to stringify and dump extent state flags when tests fail.

`test_find_first_clear_extent_bit()` validates empty-tree behavior, holes before/between/after set ranges, searching from inside set ranges, partial flag searches, and beyond-last-range behavior for `btrfs_find_first_clear_extent_bit()`.

Extent-buffer bitmap tests use a parallel kernel bitmap as oracle. They validate full clear/set, same-byte operations, cross-byte operations, cross-page operations when nodesize exceeds PAGE_SIZE, and a deterministic pseudo-random bit pattern.

`test_eb_mem_ops()` compares extent-buffer contents to normal memory after write, memcpy, and memmove operations. It covers same-page non-overlap, same-page overlap, and cross-page non-overlap/overlap cases.

`btrfs_test_extent_io()` runs delalloc, clear-bit, bitmap, and memory-operation tests in sequence.
