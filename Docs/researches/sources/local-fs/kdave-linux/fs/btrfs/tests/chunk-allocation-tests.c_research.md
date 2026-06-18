# File Research: sources/local-fs/kdave-linux/fs/btrfs/tests/chunk-allocation-tests.c

This file tests chunk allocator pending-extent helpers that operate on the device allocation-state bitmap.

`struct pending_extent_test_case` defines scenarios for `btrfs_find_hole_in_pending_extents()`: input hole range, minimum hole size, up to two pending extents, and expected hole result.

`find_hole_tests[]` covers no pending extents, pending extents at/overlapping range boundaries, multiple holes, exact-sized holes, too-small holes, fully allocated ranges, pending extents at the end, and zero-length input.

`test_find_hole_in_pending()` creates dummy fs/device state, marks pending extents with `CHUNK_ALLOCATED`, calls the helper under `chunk_mutex`, validates found/start/len outputs, and clears pending bits between cases.

`struct first_pending_test_case` and `first_pending_tests[]` cover `btrfs_first_pending_extent()`, including no match, match at search start, overlapping start, inside range, outside range, and overlapping search end.

`test_first_pending_extent()` validates returned pending start/end ranges and clears allocation-state bits between cases.

`btrfs_test_chunk_allocation()` runs first-pending tests and then hole-finding tests for each sectorsize/nodesize combination supplied by the main harness.
