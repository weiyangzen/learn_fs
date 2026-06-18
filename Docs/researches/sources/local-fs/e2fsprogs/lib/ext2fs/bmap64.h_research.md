# File Research: sources/local-fs/e2fsprogs/lib/ext2fs/bmap64.h

Defines the private 64-bit generic bitmap structure and backend operation table used by libext2fs. This header is the common contract implemented by `blkmap64_ba.c` and `blkmap64_rb.c`.

Key structures:
- `struct ext2_bmap_statistics`: optional bitmap operation counters and locality statistics.
- `struct ext2fs_struct_generic_bitmap_64`: magic, filesystem pointer, backend ops, flags, logical start/end, real end, cluster bits, description, private backend data, and base error code.
- `struct ext2_bitmap_ops`: backend vtable for allocation, free, copy, resize, mark/unmark/test, extent operations, raw range import/export, clear, stats, and first-set/first-zero search.

Macros:
- `EXT2FS_IS_32_BITMAP`
- `EXT2FS_IS_64_BITMAP`

Exports:
- `ext2fs_blkmap64_bitarray`
- `ext2fs_blkmap64_rbtree`

Implementation notes:
- Backends may leave first-set/first-zero NULL so generic code can provide fallback behavior.
- `real_end` allows padding bits beyond logical `end`.
- `cluster_bits` lets bitmap users represent cluster-addressed maps.
