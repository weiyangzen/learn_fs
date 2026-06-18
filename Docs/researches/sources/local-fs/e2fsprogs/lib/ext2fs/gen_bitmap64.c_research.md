# File Research: sources/local-fs/e2fsprogs/lib/ext2fs/gen_bitmap64.c

## Role

Implements 64-bit generic bitmap front-end logic with pluggable storage backends.

## Main Flow

- `ext2fs_alloc_generic_bmap()` chooses bitarray, rbtree, or auto-directory backend and initializes `ext2fs_struct_generic_bitmap_64`.
- Free, copy, resize, fudge-end, start/end accessors, clear, mark, unmark, test, range get/set, compare, and padding calls dispatch through `bitmap_ops`.
- Block range operations convert block ranges to cluster ranges when `cluster_bits` is set.
- Search helpers find first zero/set bit using backend acceleration when available.
- Count helpers calculate used blocks/clusters from the block bitmap.

## Important Details

- `EXT2FS_BMAP64_AUTODIR` uses `ext2fs_get_num_dirs()` to choose rbtree for sparse directory-like workloads or bitarray otherwise.
- Block bitmaps store cluster granularity by shifting arguments by `cluster_bits`.
- Statistics hooks exist under `ENABLE_BMAP_STATS` and can print when `E2FSPROGS_BITMAP_STATS` is safely set.
- 32-bit bitmap compatibility is handled by detecting old magic values and forwarding to `gen_bitmap.c`.

## Dependencies

Uses `bmap64.h` backend operation tables (`ext2fs_blkmap64_bitarray`, `ext2fs_blkmap64_rbtree`), `get_num_dirs.c`, safe getenv, and 32-bit bitmap functions.

## Risks / Notes

- Some range APIs return `EINVAL` but also use warning codes named for mark/unmark/test; callers should not rely on warning class for semantics.
- `ext2fs_compare_generic_bmap()` iterates one bit at a time for 64-bit maps, which can be expensive for large dense filesystems.
