# File Research: sources/local-fs/e2fsprogs/e2fsck/pass5.c

This file implements e2fsck pass 5, which reconciles computed block/inode usage maps with on-disk bitmaps and group/superblock summary counters.

Main entry point:
- `e2fsck_pass5(e2fsck_t ctx)` reads bitmaps, checks block bitmaps, inode bitmaps, bitmap tail padding, metadata checksums, then frees pass-5 maps: `inode_used_map`, `inode_dir_map`, `block_found_map`, and `block_metadata_map`.

Block bitmap checking:
- `check_block_bitmaps()` compares `ctx->block_found_map` against `fs->block_map`.
- It validates bitmap endpoints before scanning.
- It groups adjacent mismatches into compact single/range problem reports via `print_bitmap_problem()`.
- It has a fast path that compares entire group bitmap buffers with `memcmp` when not discarding and not on the last group.
- It handles bigalloc cluster conversions via `B2C`, `C2B`, and cluster comparison macros.
- If repairs are accepted through `PR_LATCH_BBITMAP`, it replaces `fs->block_map` with `block_found_map`, sets padding, marks the block bitmap dirty, and rescans counts.
- It updates per-group and superblock free-block counters.

Inode bitmap checking:
- `check_inode_bitmaps()` compares `ctx->inode_used_map` against `fs->inode_map`.
- It validates bitmap endpoints, handles groups marked `EXT2_BG_INODE_UNINIT`, counts free inodes and directory inodes, and repairs mismatches through `PR_LATCH_IBITMAP`.
- It updates per-group free-inode counts, used-directory counts, and the superblock free-inode count.
- It also supports discard of unused inode-table ranges when safe.

Discard support:
- `e2fsck_discard_blocks()` disables discard if the filesystem has already changed or if discard fails.
- `e2fsck_discard_inodes()` maps unused inode ranges to full inode-table blocks and discards only when discard zeroes data.

Checksum and padding checks:
- `check_inode_bitmap_checksum()` and `check_block_bitmap_checksum()` verify metadata checksums when `metadata_csum` is enabled and the bitmap has not already been dirtied.
- `check_inode_end()` and `check_block_end()` temporarily extend bitmap ends to verify padding bits past real inode/block ranges and mark bitmaps dirty when tail padding must be fixed.

Integration points:
- Relies on pass 1/2 maps as truth: `block_found_map`, `inode_used_map`, `inode_dir_map`.
- Uses `problem.c` latches for batch bitmap fixes and summary-counter repairs.
- Uses ext2fs bitmap copy, range extraction, padding, checksum, group descriptor, and dirty-marking APIs.
- Emits progress over two group-count spans: block pass then inode pass.

Risk notes:
- If bitmap replacement allocation/copy fails, pass 5 raises fatal copy errors.
- Any bitmap mismatch disables discard to avoid discarding blocks on a corrupt filesystem.
- Uninitialized group flags are cleared only after a prompted fix when live usage is found.
- Counter rescans after bitmap replacement are necessary because the first scan observed the old on-disk bitmap.
