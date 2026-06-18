# File Research: sources/os/linux/linux/fs/btrfs/tests/chunk-allocation-tests.c

Read completely: 476 lines.

This file unit-tests chunk allocator pending-extent search helpers:
- `btrfs_find_hole_in_pending_extents()`
- `btrfs_first_pending_extent()`

The tests create dummy fs_info and a dummy device, mark pending chunk-allocation ranges in the device `alloc_state` extent tree with `CHUNK_ALLOCATED`, and validate search results under `fs_info->chunk_mutex`.

`find_hole_tests[]` covers:
- no pending extents
- pending extent at or overlapping the search start
- first, second, or third hole satisfying minimum size
- all holes too small, with expected largest-hole reporting
- full search range consumed by pending allocation
- pending extent at the end of the range
- zero-length input

`test_find_hole_in_pending()` validates both the boolean found result and adjusted `hole_start`/`hole_len`, then clears all pending bits after each case.

`first_pending_tests[]` covers:
- no pending extent
- pending extent at search start
- pending extent overlapping search start
- pending extent inside the search range
- pending extent outside the search range
- pending extent overlapping the end of the search range

`test_first_pending_extent()` validates found status plus returned pending start/end.

`btrfs_test_chunk_allocation()` runs first-pending tests before hole-finding tests.

Correctness focus:
- Pending extent searches must correctly clip and report ranges around already-reserved chunk-allocation spans.
- The helpers are tested with large GiB-scale ranges to exercise boundary arithmetic.
- Extent-state cleanup after each case prevents one table row from contaminating the next.
