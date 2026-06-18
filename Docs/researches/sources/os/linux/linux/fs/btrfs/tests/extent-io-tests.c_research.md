# File Research: sources/os/linux/linux/fs/btrfs/tests/extent-io-tests.c

Read completely: 830 lines.

This file tests selected extent I/O tree, folio locking, extent-buffer bitmap, clear-range, and extent-buffer memory operations.

`test_find_delalloc()`:
- Creates dummy fs_info/root/inode and an inode io-tree.
- Allocates and dirties pages covering two `BTRFS_MAX_EXTENT_SIZE` ranges.
- Exercises `find_lock_delalloc_range()` over scenarios where the search matches the whole delalloc range, starts inside it, starts after it, spans a later range, and encounters a dirty-page gap.
- Uses `process_page_range()` to verify pages in returned ranges are locked, then unlocks/releases them.
- Dumps the extent I/O tree on failure.

Extent-state diagnostics:
- `extent_flag_to_str()` and `dump_extent_io_tree()` format extent-state flags for test failures.

Extent-buffer bitmap tests:
- `check_eb_bitmap()` compares an ordinary Linux bitmap with bits read through `extent_buffer_test_bit()`.
- `test_bitmap_set()` and `test_bitmap_clear()` mirror operations into both representations.
- `__test_eb_bitmaps()` covers full clear/set, same-byte partial operations, cross-byte operations, cross-page operations when nodesize exceeds PAGE_SIZE, and a pseudo-random bit pattern.
- `test_eb_bitmaps()` runs the bitmap suite on dummy extent buffers starting at both 0 and a sectorsize-aligned nonzero bytenr.

`test_find_first_clear_extent_bit()`:
- Tests `btrfs_find_first_clear_extent_bit()` on an empty tree, beginning holes, holes between allocated/trimmed ranges, ranges missing only one requested flag, and searches beyond the last known range.

Extent-buffer memory operations:
- `test_eb_mem_ops()` initializes an extent buffer and memory buffer with random bytes, then mirrors `memcpy_extent_buffer()` and `memmove_extent_buffer()` against normal `memcpy()`/`memmove()`.
- It covers same-page non-overlapping copies, same-page overlapping moves, and cross-page cases for larger nodesizes.

`btrfs_test_extent_io()` runs delalloc discovery, clear-bit search, bitmap tests, and memory-operation tests.

Correctness focus:
- Delalloc range discovery must return correct byte ranges and lock all corresponding pages.
- Extent-buffer bitmap helpers must be byte/bit correct across unaligned and page-spanning ranges.
- Extent-buffer copy/move helpers must match normal memory semantics even when the buffer spans folios.
