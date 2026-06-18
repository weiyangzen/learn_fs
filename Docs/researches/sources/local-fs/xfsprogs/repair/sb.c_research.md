# File Research: sources/local-fs/xfsprogs/repair/sb.c

Handles superblock validation, primary superblock recovery from secondaries, geometry voting, and primary superblock writes.

Core flow:
- `verify_sb` validates superblock magic, version, in-progress flag, sector size/logs, CRC, block size, filesystem geometry, inode geometry, log geometry, realtime geometry, inode alignment, inode percentage, stripe settings, directory block size, metadata directory padding, and rtgroup geometry.
- `find_secondary_sb` tries to locate a valid secondary superblock using current geometry, guessed default geometry, and finally brute-force scanning.
- `__find_secondary_sb` scans the device in large buffers, checks candidate superblocks every basic block, and verifies them by calling `verify_set_primary_sb`.
- `verify_set_primary_sb` reads secondary superblocks, builds a geometry vote list, requires enough agreement, optionally force-accepts weak cases, and copies the best geometry into the primary candidate.
- `copy_sb` copies only fields that should be common between primary and secondary superblocks, preserving primary-only inode pointers and version bits.
- `write_primary_sb` writes a primary superblock buffer and recalculates CRC when needed.
- `get_sb` reads and validates a superblock at a specific offset.
- Geometry helpers build and compare `fs_geometry_t` records.

Important behavior:
- Two-AG and one-AG filesystems require `force_geometry` when geometry cannot be independently validated.
- Metadata-directory filesystems cause a warning that quota accounting/enforcement flags can be lost when recovering from a secondary.
- Realtime group validation checks rg count/extents, rextsize, maxes, required exchange feature, and computed rg block log.
