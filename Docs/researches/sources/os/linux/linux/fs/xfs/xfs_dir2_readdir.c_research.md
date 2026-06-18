# File Research: sources/os/linux/linux/fs/xfs/xfs_dir2_readdir.c

Implements XFS directory iteration for shortform, block, leaf, and node directory formats.

Key behavior:
- `xfs_dir3_get_dtype` maps XFS on-disk file type values to VFS `DT_*`, returning `DT_UNKNOWN` when file type support is unavailable or invalid.
- Shortform readdir emits `.` and `..`, then local entries from the inode data fork, checking names for corruption.
- Block directory readdir reads the single directory data block, unlocks the inode while emitting entries, skips unused records, validates names, and advances `ctx->pos`.
- Leaf/node readdir scans mapped data blocks up to `XFS_DIR2_LEAF_OFFSET`, using extent lookup and a sliding readahead window to reduce I/O stalls.
- `xfs_readdir` dispatches based on directory format after shutdown/zapped-fork checks and records getdents statistics.

The code carefully manages inode data-map locks around buffer reads and user emission, and marks directory/attribute health sick on name-format corruption.
