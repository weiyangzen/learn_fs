# File Research: sources/os/linux/linux/fs/btrfs/tests/free-space-tests.c

Read completely: 1063 lines.

This file tests the in-memory free-space cache used by block groups.

`test_extents()` covers extent-entry-only behavior:
- Add and remove an entire extent.
- Remove from tail, front, and middle.
- Verify removed ranges no longer exist.

`test_bitmaps()` covers bitmap-entry-only behavior:
- Add bitmap free space and remove it entirely.
- Remove a middle chunk.
- Add a free range straddling two bitmap regions and remove an overlapping portion.

`test_bitmaps_and_extents()` covers mixed representation:
- Extent and bitmap entries at related offsets.
- Removing from extent while bitmap remains.
- Removing from bitmap while extent remains.
- Removing overlapping ranges represented by both extent and bitmap entries.
- Cases where an extent starts before a bitmap and deletion falls inside both.
- A regression where removal spanning bitmap plus extent should not leak `-EAGAIN`.

Bitmap-to-extent stealing:
- `test_steal_space_from_bitmap_to_extent()` temporarily overrides `free_space_ctl->op->use_bitmap` to force bitmap use after an extent exists.
- It constructs adjacent extent/bitmap representations that together form a larger free range.
- It verifies that contiguous bitmap free space can be stolen into an extent entry so a 1 MiB allocation can be satisfied from a single entry.
- It tests both directions: extent on the left of bitmap and extent on the right of bitmap.
- It verifies unrelated small bitmap free ranges are not accidentally stolen.
- `check_cache_empty()` ensures allocation drains all free space and leaves no entries.

Bytes index:
- `test_bytes_index()` validates `free_space_bytes` ordering by descending bytes for extent entries and bitmap entries.
- It tests bitmap entries where total bytes and `max_extent_size` differ, forcing `btrfs_find_space_for_alloc()` to recalculate and reorder the bytes index.
- It verifies later additions reindex by total bytes and allocation selects the expected bitmap.

`btrfs_test_free_space_cache()` creates dummy fs_info, a block group large enough to cross bitmap boundaries even on large-page systems, inserts an extent-tree root, and runs all free-space-cache suites.

Correctness focus:
- Free-space cache operations must remove exactly the requested ranges across extent and bitmap representations.
- Mixed representation must not leave duplicate or stale free ranges.
- Large allocations must not fail just because contiguous free space is split between bitmap and extent entries.
- The bytes index must reflect either total bytes or max contiguous extent size at the correct times.
