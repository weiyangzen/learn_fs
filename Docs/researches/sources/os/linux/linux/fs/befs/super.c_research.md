# File Research: sources/os/linux/linux/fs/befs/super.c

## Purpose
Loads and validates BeFS superblock metadata.

## Main Functions
- `befs_load_sb()`:
  - detects disk byte order from `fs_byte_order`
  - converts disk superblock fields into `struct befs_sb_info`
  - converts log, root, and indices block runs
  - initializes `nls` to `NULL`
- `befs_check_sb()`:
  - validates all three BeFS magic values
  - accepts block sizes 1024, 2048, 4096, or 8192
  - rejects block sizes larger than `PAGE_SIZE`
  - verifies `1 << block_shift == block_size`
  - logs inconsistency if `ag_shift` disagrees with `blocks_per_ag`
  - rejects dirty or journal-nonempty filesystems

## Research Notes
The driver refuses to mount unclean BeFS volumes and instructs users to boot BeOS and mount the volume to clean the journal. This matches the driver’s read-only/non-journal-replay design.
