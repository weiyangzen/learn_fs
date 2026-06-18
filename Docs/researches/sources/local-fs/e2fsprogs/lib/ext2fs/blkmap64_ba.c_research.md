# File Research: sources/local-fs/e2fsprogs/lib/ext2fs/blkmap64_ba.c

Implements the flat bitarray backend for `ext2fs_generic_bitmap_64`. The backend stores one contiguous byte array in `struct ext2fs_ba_private_struct` and exports it through `ext2fs_blkmap64_bitarray`.

Core operations allocate, free, copy, resize, mark, unmark, test, range mark/unmark, clear-range test, set/get raw ranges, clear the whole bitmap, print optional stats, and find first set/zero bits.

Behavior details:
- Allocation size is `((real_end - start) / 8) + 1`.
- Mark/test/unmark subtract `bitmap->start` before accessing raw bits.
- Resize clears newly exposed bits when growing and resizes backing memory when `real_end` changes.
- `ba_test_clear_bmap_extent` checks partial first/last bytes and uses `ext2fs_mem_is_zero` for full bytes.
- First-set and first-zero scans optimize alignment, then scan 64-bit chunks, bytes, and trailing bits.

Dependencies: `ext2fsP.h`, `bmap64.h`, raw bitops from `bitops.c/h`, libext2fs memory allocation helpers.

Implementation notes:
- `ba_set_bmap_range` and `ba_get_bmap_range` copy raw packed bitmap bytes starting at `start >> 3`; callers are expected to pass range offsets in the backend’s expected coordinate system.
- This backend is memory-heavy but simple and fast for dense bitmaps.
- It is selected through the `struct ext2_bitmap_ops` vtable with type `EXT2FS_BMAP64_BITARRAY`.
