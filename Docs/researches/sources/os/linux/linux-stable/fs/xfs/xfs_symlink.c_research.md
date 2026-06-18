# File Research: sources/os/linux/linux-stable/fs/xfs/xfs_symlink.c

Implements XFS symlink read, creation, and inactive-time cleanup.

Key entry points:
- `xfs_readlink`
- `xfs_symlink`
- `xfs_inactive_symlink`

Readlink behavior:
- Rejects reads after shutdown or if the data fork is zapped.
- Takes `XFS_ILOCK_SHARED`.
- Validates symlink length is nonzero and at most `XFS_SYMLINK_MAXLEN`.
- For inline symlinks (`XFS_DINODE_FMT_LOCAL`), validates `if_data` and copies the target including terminator.
- For remote symlinks, delegates to `xfs_symlink_remote_read`.
- Marks the inode symlink health sick and returns `-EFSCORRUPTED` on corruption.

Symlink creation flow:
- Builds inode creation arguments for `S_IFLNK` plus requested mode bits.
- Validates target path length.
- Allocates quota records with `xfs_icreate_dqalloc`.
- Decides whether the target can fit inline. If parent pointers are enabled, it reserves remote/attribute-related space as needed.
- Starts parent pointer arguments, allocates an inode-create transaction, locks the parent directory, and rejects creation if `XFS_DIFLAG_NOSYMLINKS` is set.
- Allocates and initializes the symlink inode.
- Joins the parent directory to the transaction, attaches dquots, writes the symlink target through `xfs_symlink_write_target`, updates VFS inode size, and creates the directory entry through `xfs_dir_create_child`.
- Marks the transaction synchronous for wsync/dirsync mounts.
- On success, commits, releases dquots, returns the locked-created inode through `ipp`, unlocks inode and parent, and finalizes parent pointer state.
- Error paths cancel transactions, finish/release partially created inodes after abort, finish parent pointer state, release dquots, and unlock the parent if still needed.

Inactive cleanup:
- Inline symlinks need no special cleanup because fork state is removed by inode free.
- Remote symlinks are cleaned by `xfs_inactive_symlink_rmt`.
- `xfs_inactive_symlink_rmt` asserts remote symlinks have one or two extents, starts an itruncate transaction, sets size to zero, changes mode to regular file to avoid writing an invalid zero-length symlink to disk, logs the inode core, truncates remote symlink blocks, commits, and drops in-memory extent descriptions.
- Corrupt symlink lengths during inactive handling mark the symlink sick and return `-EFSCORRUPTED`.

Important dependencies:
- Remote storage helpers are in `xfs_symlink_remote.h`.
- Parent pointer lifecycle uses `xfs_parent_start` and `xfs_parent_finish`.
- Directory entry creation uses `xfs_dir_create_child`.
- Quota attachment uses quota helpers from `xfs_quota.h`.

Research notes:
- The mode flip to regular file during remote symlink cleanup is intentional verifier protection, not a user-visible change.
- Parent pointer support changes space reservation decisions for symlink creation.
- Lock and transaction ownership transitions are subtle after inode allocation because allocation can commit/release earlier transaction state.
