# File Research: sources/local-fs/ocfs2-tools/fswreck/inode.c

This file creates inode, inline-data, orphan, allocation, refcount-flag, metadata-ECC, and duplicate-cluster corruptions.

Key behavior:
- `damage_inode()` mutates a target inode field based on `fsck_type`, including generation, block number, delete time, suballoc slot, size, sparse size/clusters, link count, metadata ECC, valid flag, refcount feature flag, and refcount location.
- `mess_up_inode_field()` creates a file under the supplied directory, optionally prepares sparse/allocated state, feature-gates refcount scenarios, then calls `damage_inode()`.
- `mess_up_inode_not_connected()` allocates a regular inode without linking it.
- `mess_up_inode_orphaned()` creates a file under a slot orphan directory.
- `mess_up_inode_alloc()` allocates an inode and clears `OCFS2_VALID_FL`.
- `mess_up_inline_flag()` sets inline-data flags on regular file and directory inodes on a volume that does not support inline data.
- `mess_up_inline_inode()` creates inline regular and directory inodes, then corrupts `id_count`, `i_size`, or `i_clusters`.
- `mess_up_dup_clusters()` creates duplicate cluster ownership between two regular files or between a regular file and the journal system file.

Integration notes:
- Reuses `create_file()` and `create_directory()`.
- Uses `ocfs2_write_inode_without_meta_ecc()` specifically to preserve bad ECC for `INODE_BLOCK_ECC`.
- Many paths are feature-sensitive and intentionally abort if run against the wrong mkfs feature set.
