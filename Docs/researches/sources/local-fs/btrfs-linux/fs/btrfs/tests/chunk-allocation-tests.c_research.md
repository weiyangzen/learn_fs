# File Research: sources/local-fs/btrfs-linux/fs/btrfs/tests/chunk-allocation-tests.c

This file tests chunk allocator pending-extent helpers, specifically `btrfs_find_hole_in_pending_extents()` and `btrfs_first_pending_extent()`. These helpers operate on a device allocation-state extent-io tree and are central to avoiding overlap with chunk allocations already pending.

`find_hole_tests[]` defines table-driven scenarios for searching holes inside a candidate range while some ranges are marked `CHUNK_ALLOCATED`. It covers no pending extents, pending extents at or overlapping the start/end, two-hole and three-hole layouts, cases where the first/second/third hole is the first acceptable result, all holes too small while still returning the largest candidate, fully allocated ranges, and zero-length input.

`test_find_hole_in_pending()` builds a dummy fs_info and dummy device, marks each test case's pending extents in `device->alloc_state`, calls `btrfs_find_hole_in_pending_extents()` under `fs_info->chunk_mutex`, validates both the found boolean and adjusted start/length, then clears all pending bits before the next case.

`first_pending_tests[]` covers direct lookup of the first pending extent overlapping a search range. It includes no pending extent, pending at search start, overlap with search start, pending inside the search range, outside the range, and overlap with the end.

`test_first_pending_extent()` mirrors the table-driven setup, marks one pending extent if present, calls `btrfs_first_pending_extent()` under `chunk_mutex`, and validates returned start/end only when a pending extent is expected.

`btrfs_test_chunk_allocation()` runs the first-pending tests before the hole-search tests. The file uses dummy fs/device helpers from `btrfs-tests.c` and intentionally validates exact range transformations, not just success/failure.
