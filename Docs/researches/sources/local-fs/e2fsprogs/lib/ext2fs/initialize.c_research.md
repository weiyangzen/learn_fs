# File Research: sources/local-fs/e2fsprogs/lib/ext2fs/initialize.c

## Role

Initializes a new in-memory filesystem handle and superblock/group metadata from mke2fs-style parameters.

## Main Flow

- `ext2fs_initialize()` allocates `ext2_filsys`, opens the I/O manager, creates the superblock, derives block/cluster geometry, feature defaults, timestamps, inode counts, group counts, descriptor blocks, reserved GDT blocks, and metadata overhead.
- Handles bigalloc, 64-bit descriptors, sparse superblock variants, resize inode, meta_bg fallback, reserved blocks, fake time environment variables, and journal-device-only initialization.
- Allocates block/inode bitmaps and group descriptor memory.
- Reserves superblock/GDT blocks per group and initializes group free counts, inode unused counts, flags, checksums, and dirty bits.
- `ext2fs_calculate_summary_stats()` recomputes free block/inode counters and lazy-init flags from current bitmaps.

## Dependencies

Uses safe getenv, I/O manager open/set blocksize, bitmap allocation, group descriptor helpers, superblock feature helpers, `ext2fs_reserve_super_and_bgd2`, and `ext2fs_free()` cleanup.

## Risks / Notes

- Many parameter corrections are silent, such as shrinking last too-small groups or clamping sparse-super backup groups.
- The function accounts for bitmaps/inode tables but does not place all final metadata; later allocation routines complete layout.
- Environment-controlled time is gated through `ext2fs_safe_getenv()`.
