# File Research: sources/local-fs/e2fsprogs/e2fsck/super.c

## Purpose
Performs e2fsck pass-0 style superblock, group descriptor, orphan, resize-inode, quota, timestamp, feature, and backup-superblock checks before or around the main filesystem passes.

## Main Elements
- `check_super_value()` / `check_super_value64()`: validate scalar superblock fields against min, max, and power-of-two constraints; corrupt values set abort.
- Orphan cleanup:
  - `release_inode_block()` frees or truncates blocks for orphaned inodes and updates quota/accounting.
  - `release_inode_blocks()` iterates direct/indirect inode blocks and extended attribute block references.
  - `e2fsck_read_all_quotas()` / `e2fsck_write_all_quotas()` load and persist quota state around orphan cleanup.
  - `release_orphan_inode()` clears or truncates a single inode from the orphan list.
  - `process_orphan_block()` and `process_orphan_file()` validate orphan-file blocks, checksums, and listed inodes.
  - `release_orphan_inodes()` processes legacy orphan list and ext4 orphan file when safe.
- Orphan file reinitialization:
  - `reinit_orphan_block()` rewrites clean orphan-file block templates and updates checksums.
  - `check_init_orphan_file()` verifies, clears, or reports corrupted orphan-file state.
- `check_resize_inode()`: validates the resize inode, reserved GDT block layout, and incompatible feature combinations.
- `e2fsck_fix_dirhash_hint()`: sets signed/unsigned hash hint for indexed directories.
- `check_super_block()`: core superblock and descriptor validation routine.
- `check_backup_super_block()`: compares selected primary fields against the first valid backup superblock, ignoring known kernel-mutated flags.

## Control Flow
`check_super_block()` allocates invalid bitmap/table flag arrays, validates superblock geometry, checks feature compatibility rules, validates every group descriptor’s metadata block locations and checksums, recomputes free counters, optionally adds UUID/testfs/revision fixes, clears or processes orphan structures, adjusts tolerated time skew, validates quotas, journal hints, dirhash hints, and hidden quota inodes.

## Dependencies And Integration
Uses e2fsck problem handling (`fix_problem`, `problem_context`), libext2fs bitmap/group descriptor APIs, quota support, journal helpers, orphan-file helpers, and UUID support. It is invoked from `unix.c` after filesystem open, feature checks, and MMP/journal setup.

## Risk Notes
This file makes destructive repairs: orphan cleanup frees blocks/inodes, group descriptor fixes clear metadata locations, and resize/orphan-file repairs can rewrite special inodes. Many paths are guarded by read-only checks and `fix_problem()` policy, but correctness depends on trustworthy bitmaps and descriptor checksums.
