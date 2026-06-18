# File Research: sources/os/linux/linux-stable/fs/xfs/xfs_iops.c

This file implements VFS inode operations for XFS: create, lookup, link, unlink, symlink, rename, getattr, setattr, update_time, fiemap, tmpfile, DAX inode setup, and Linux inode initialization.

Creation and namespace operations:
- `xfs_generic_create` is the common path for regular file, directory, special file, and tmpfile creation.
  - Validates device numbers for special files.
  - Creates POSIX ACLs.
  - Predicts whether xattrs are needed for ACL/security setup.
  - Calls `xfs_create` or `xfs_create_tmpfile`.
  - Initializes security xattrs and ACLs after inode creation.
  - Sets inode operations and instantiates the dentry or tmpfile.
  - Cleans up the inode if post-create xattr/ACL setup fails.
- Wrappers implement `mknod`, `create`, `mkdir`, and `tmpfile`.
- `xfs_vn_lookup` performs normal lookup; `xfs_vn_ci_lookup` performs ASCII case-insensitive lookup and uses `d_add_ci` for casefolded names.
- `xfs_vn_link`, `xfs_vn_unlink`, `xfs_vn_symlink`, and `xfs_vn_rename` translate VFS dentries to `xfs_name` and call core XFS namespace operations.

Security/xattr setup:
- `xfs_initxattrs` writes initial security xattrs via `xfs_attr_change`.
- `xfs_inode_init_security` invokes LSM security initialization.
- `xfs_create_need_xattr` predicts whether inode allocation should initialize an attr fork.

Stat and attribute reporting:
- `xfs_vn_getattr` fills `kstat`, including size, ownership through idmapped mounts, birth time, block count, immutable/append/nodump flags, block size, DIO alignment, and atomic write limits.
- `xfs_report_dioalign` reports separate read/write DIO alignment for CoW files.
- `xfs_get_atomic_write_min`, `xfs_get_atomic_write_max`, and `xfs_get_atomic_write_max_opt` report hardware/software atomic write capabilities.

Setattr and truncation:
- `xfs_vn_change_ok` checks readonly, shutdown, and VFS permission constraints.
- `xfs_setattr_nonsize` handles mode, uid/gid, timestamps, quota transfer, inode logging, and ACL chmod updates.
- `xfs_vn_setattr_size` handles truncation and extension:
  - Requires IOLOCK/MMAPLOCK exclusivity.
  - Attaches dquots.
  - Waits for direct I/O.
  - Reserves zoned space when needed.
  - Zeroes exposed EOF ranges or partial truncate blocks.
  - Updates page cache size before transaction.
  - Writes dirty beyond-disk-size data to avoid stale/null file exposure.
  - Allocates truncate transaction, logs new disk size, truncates extents on shrink, clears EOF block tags, copies attrs, and commits.
- `xfs_vn_setattr` routes size vs non-size updates and breaks layouts for size changes.

Time and fiemap:
- `xfs_vn_update_time` handles lazytime and transactional timestamp logging.
- `xfs_vn_sync_lazytime` forces timestamp log update for lazytime inodes.
- `xfs_vn_fiemap` dispatches to xattr or read iomap ops.

Inode operation tables:
- `xfs_inode_operations` for regular/special inodes.
- `xfs_dir_inode_operations` for normal directories.
- `xfs_dir_ci_inode_operations` for ASCII case-insensitive directories.
- `xfs_symlink_inode_operations` for symlinks.

Inode setup:
- `xfs_inode_supports_dax` and `xfs_inode_should_enable_dax` decide DAX capability and policy.
- `xfs_diflags_to_iflags` maps XFS flags to VFS `i_flags`, setting `S_DAX` only during initialization.
- `xfs_setup_inode` initializes Linux inode state, fake hash, size, flags, metadata-private state, lockdep classes, GFP_NOFS mapping mask, realtime stable writes, and no-xattr/no-ACL hints.
- `xfs_setup_iops` installs inode/file/address-space operations based on inode mode and DAX state.

Risk notes:
- Truncate ordering is critical to avoid stale data exposure after crash.
- Creation cleanup must undo namespace entries if security/ACL initialization fails.
- DAX flag transitions are intentionally conservative because active access paths cannot safely change `S_DAX`.
