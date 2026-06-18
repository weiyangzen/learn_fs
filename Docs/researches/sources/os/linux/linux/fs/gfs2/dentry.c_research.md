# File Research: sources/os/linux/linux/fs/gfs2/dentry.c

Defines GFS2 dentry operations for clustered lookup validation, filesystem-specific hashing, and deletion decisions.

Key entry points:
- `gfs2_drevalidate()`
- `gfs2_dhash()`
- `gfs2_dentry_delete()`
- `gfs2_dops`

Important control flow:
- Revalidation rejects RCU mode with `-ECHILD`.
- For cluster-locking mounts, it acquires the parent directory glock in shared mode unless already held and checks the name/inode pair with `gfs2_dir_check()`.
- Negative dentries are valid only if the name still returns `-ENOENT`.
- Hashing uses GFS2’s on-disk CRC32-based directory hash.
- Dentry deletion returns true when the inode’s iopen glock is being demoted.

Dependencies and integration:
- Uses GFS2 glocks, directory lookup validation, inode state, and VFS dentry operations.

Risks and invariants:
- In nolock/local mode, dentries are considered valid without distributed lookup recheck.
- Bad inodes invalidate dentries.
