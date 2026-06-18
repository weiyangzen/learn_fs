# File Research: sources/os/linux/linux/fs/xfs/xfs_symlink.c

## Purpose

`xfs_symlink.c` implements XFS symlink read, create, and inactive-time cleanup. It handles both inline symlink targets stored in the inode data fork and remote symlink targets stored in filesystem blocks.

## Main Interfaces

- `xfs_readlink(struct xfs_inode *ip, char *link)`: reads a symlink target into the caller-provided buffer.
- `xfs_symlink(struct mnt_idmap *idmap, struct xfs_inode *dp, struct xfs_name *link_name, const char *target_path, umode_t mode, struct xfs_inode **ipp)`: creates a symlink inode and directory entry transactionally.
- `xfs_inactive_symlink(struct xfs_inode *ip)`: frees remote symlink blocks during inode inactivation.
- `xfs_inactive_symlink_rmt(struct xfs_inode *ip)`: helper for remote symlink truncation.

## Read Path

- `xfs_readlink` traces the operation, rejects shutdown mounts and zapped data forks, then locks the inode shared.
- It validates `i_disk_size` against zero, negative values, and `XFS_SYMLINK_MAXLEN`.
- Inline symlinks require non-null `ip->i_df.if_data`; missing data is treated as corruption and marks the inode sick.
- Remote symlinks are read through `xfs_symlink_remote_read`.
- Corruption paths unlock, mark `XFS_SICK_INO_SYMLINK`, and return `-EFSCORRUPTED`.

## Create Path

- `xfs_symlink` initializes inode creation args with the idmap, parent inode, and symlink mode.
- It rejects shutdown mounts and targets whose string length is `>= XFS_SYMLINK_MAXLEN`.
- It allocates quota records with `xfs_icreate_dqalloc`.
- It decides whether the target can fit inline. If parent pointers are enabled or the target exceeds inline capacity, it reserves remote symlink blocks.
- It starts parent pointer context, allocates an inode creation transaction, and locks the parent directory with parent locking semantics.
- It rejects creation under directories with `XFS_DIFLAG_NOSYMLINKS`.
- It allocates and creates the symlink inode, joins the parent directory to the transaction, attaches dquots, writes the target through `xfs_symlink_write_target`, updates VFS inode size, and creates the directory entry with `xfs_dir_create_child`.
- Synchronous or dirsync mounts force the transaction to disk before returning.
- Successful completion commits the transaction, releases dquots, returns the new inode locked state correctly unwound, unlocks parent and child, finishes parent pointer state, and returns the new inode through `ipp`.

## Inactive Cleanup

- `xfs_inactive_symlink` validates symlink length under exclusive inode lock.
- Inline symlinks require no explicit cleanup because inode deletion frees local fork state.
- Remote symlinks call `xfs_inactive_symlink_rmt`.
- `xfs_inactive_symlink_rmt` asserts remote extents are already readable and limited to one or two extents, starts an itruncate transaction, changes the inode size to zero and type to regular file to avoid writing zero-length symlinks to disk, truncates remote symlink blocks, commits, and drops in-memory extent descriptions.

## Error Handling

- Transaction errors cancel the transaction and then finish inode setup/release carefully to avoid recursive transactions and deadlocks from `xfs_inactive`.
- Quotas and parent pointer context are released on all relevant error paths.
- Parent directory unlock on errors is guarded by `unlock_dp_on_error` because after `xfs_trans_ijoin`, transaction cancel owns unlock behavior.

## Dependencies and Callers

- Uses inode, bmap, quota, transaction, directory, parent pointer, deferred operation, health, and remote symlink helpers.
- Declared by `xfs_symlink.h` and used by XFS VFS inode operation code.

## Research Notes

- Parent pointer support changes symlink space reservation even for targets that otherwise fit inline.
- The cleanup path intentionally converts a soon-to-be-deleted symlink to a regular file after size zeroing so verifiers do not encounter a zero-length symlink on disk.
