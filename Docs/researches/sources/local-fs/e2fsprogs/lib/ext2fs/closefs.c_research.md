# File Research: sources/local-fs/e2fsprogs/lib/ext2fs/closefs.c

Handles filesystem flush and close operations, backup superblock/GDT placement, sparse-super rules, dynamic revision updates, and final resource release.

Major APIs:
- `ext2fs_bg_has_super`: determines whether a group has a backup superblock, supporting sparse_super and sparse_super2.
- `ext2fs_super_and_bgd_loc2`: computes superblock, old descriptor, meta_bg descriptor, and used-block locations for a group.
- `ext2fs_super_and_bgd_loc`: legacy 32-bit wrapper that returns an approximate free block count.
- `ext2fs_update_dynamic_rev`: upgrades old revision superblocks to dynamic revision defaults.
- `ext2fs_flush` / `ext2fs_flush2`: writes dirty bitmaps, descriptors, backup superblocks, and primary superblock.
- `ext2fs_close`, `ext2fs_close2`, `ext2fs_close_free`: flush, stop MMP, free filesystem handles.

Flush behavior:
- Writes bitmaps first because bitmap checksums live in descriptors.
- Temporarily clears valid state and journal recovery state while writing backups.
- Handles big-endian swapping through shadow superblock and descriptor buffers.
- Writes backup superblocks/descriptors unless `EXT2_FLAG_MASTER_SB_ONLY` or journal device rules suppress them.
- Writes the primary superblock last, preserving selected original fields when byte-write support exists.
- Updates `s_kbytes_written` from IO stats on close.

Implementation notes:
- `write_primary_superblock` tries byte-range writes of changed superblock words and falls back to full superblock write if unsupported.
- `ext2fs_flush2` restores the in-memory filesystem state after write attempts.
- External journal devices skip descriptor and backup-super writes.
