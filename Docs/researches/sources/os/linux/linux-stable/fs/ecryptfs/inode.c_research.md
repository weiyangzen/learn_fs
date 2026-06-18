# File Research: sources/os/linux/linux-stable/fs/ecryptfs/inode.c

## Summary
Implements eCryptfs inode operations and most namespace-changing VFS behavior. It interposes upper inodes over lower inodes, translates names through filename encryption, creates and initializes encrypted files, handles unlink/link/rename/symlink/mkdir/mknod/rmdir, translates truncation sizes, and forwards xattrs, ACLs, file attributes, permissions, and getattr/setattr to the lower filesystem.

## Main Responsibilities
- Create upper inodes with `iget5_locked()` keyed by lower inode identity.
- Reject casefolded lower directories and cross-superblock lower inodes.
- Assign inode/file operation tables by inode type.
- Interpose upper dentries over existing lower dentries during lookup and creation.
- Encrypt and encode lookup names before lower lookup when filename encryption is enabled.
- Initialize new regular files with eCryptfs metadata and generated file encryption keys.
- Encode symlink targets on creation and decode/decrypt symlink targets on read.
- Delegate namespace operations to lower VFS helpers while copying back attributes.
- Convert upper file sizes to lower encrypted sizes for truncate and expansion.
- Forward permission, getattr, setattr, xattr, ACL, and fileattr operations.

## Key APIs
- `ecryptfs_get_inode()`
- `ecryptfs_lookup()`
- `ecryptfs_create()`
- `ecryptfs_initialize_file()`
- `ecryptfs_truncate()`
- `ecryptfs_setattr()`
- `ecryptfs_main_iops`
- `ecryptfs_dir_iops`
- `ecryptfs_symlink_iops`
- `ecryptfs_xattr_handlers`

## Important Behavior
Lookup sets `d_fsdata` to the lower dentry even for negative dentries. For regular files, it reads and validates header or xattr metadata early enough to initialize upper `i_size`.

Truncation is encryption-aware. Expanding writes a single zero at the new last byte so the write path fills intermediate zeros. Shrinking zeroes the tail of the final upper page, updates encrypted metadata with the new upper size, and only truncates the lower file when the encrypted lower size actually decreases.

Most metadata changes are passed to the lower inode via `notify_change()`, but size changes go through `__ecryptfs_truncate()`. Setuid/setgid kill operations intentionally let the lower filesystem interpret mode clearing.

## Research Notes
This is the main stackable inode layer. Its core invariants are stable lower inode references, dentry lower mappings, encrypted filename translation before lower lookup/creation, and careful upper-size versus lower-size conversion for encrypted regular files.
