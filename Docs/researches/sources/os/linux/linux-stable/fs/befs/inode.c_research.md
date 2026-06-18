# File Research: sources/os/linux/linux-stable/fs/befs/inode.c

This file validates raw BeFS inodes before VFS inode population.

Export:
- `befs_check_inode()` returns `BEFS_OK` for usable inodes and `BEFS_BAD_INODE` for invalid ones.

Validation performed:
- Checks `magic1` against `BEFS_INODE_MAGIC1`.
- Converts and checks the inode’s self-reported disk address against the VFS block number being loaded.
- Verifies `BEFS_INODE_IN_USE` is set.

Integration:
- `linuxvfs.c` calls this from `befs_iget()` after reading the inode block.
- Uses `fs32_to_cpu()`, `fsrun_to_cpu()`, and `iaddr2blockno()`.

Risk notes:
- The validation is intentionally limited; it does not deeply validate mode, datastream ranges, parent address, or block-run bounds.
