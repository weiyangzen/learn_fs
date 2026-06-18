# File Research: sources/os/linux/linux-stable/fs/qnx4/inode.c

## Summary
Implements QNX4 mount, superblock validation, inode loading, extent-based block mapping, statfs, address-space operations, inode cache, and filesystem registration.

## Main Responsibilities
- Force QNX4 mounts read-only.
- Validate the root directory and locate the `.bitmap` file.
- Map logical file blocks through the first extent and chained extent blocks.
- Load raw QNX4 inode entries into Linux inodes.
- Provide read-only file, directory, and symlink behavior.
- Register/unregister the `qnx4` filesystem and inode slab cache.

## Key Interfaces
- `qnx4_block_map()` maps logical blocks to physical blocks.
- `qnx4_iget()` reads and initializes an inode.
- `qnx4_fill_super()` mounts and validates a QNX4 filesystem.
- `qnx4_statfs()` reports block/free counts and limits.
- `qnx4_get_tree()` mounts via `get_tree_bdev()`.

## Important Behavior
Block mapping treats QNX4 extent block numbers as one-based on disk, subtracting one for `sb_bread()` and adding `offset - 1` when returning a physical block from an extent. Additional extents are read from chained `qnx4_xblk` blocks with signature `IamXblk`.

Mount validation reads block 1 as the superblock, confirms the root directory name is `/`, scans the root directory for `.bitmap`, and stores a heap copy of that raw inode for later statfs.

`qnx4_iget()` maps regular files to `generic_ro_fops`, directories to QNX4 dir ops, symlinks to page symlink ops, and rejects other modes as bad inodes.

## State and Synchronization
Per-inode raw QNX4 metadata is stored in `struct qnx4_inode_info`. Per-superblock state stores version and cached bitmap inode. The inode cache is created at module init and destroyed after `rcu_barrier()`.

## Cross-File Interactions
`dir.c` and `namei.c` rely on `qnx4_block_map()` and `qnx4_iget()`. `bitmap.c` relies on the cached `.bitmap` inode established during mount.

## Risks
The implementation is read-only and intentionally minimal. Block mapping and directory traversal depend on trusting on-disk extent and directory structures after basic validation.
