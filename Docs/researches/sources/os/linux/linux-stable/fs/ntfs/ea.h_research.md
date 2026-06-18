# File Research: sources/os/linux/linux-stable/fs/ntfs/ea.h

## Scope

This header declares NTFS EA, xattr, WSL metadata, and optional POSIX ACL integration points.

## APIs And Data Structures

- `NTFS_EA_UID`, `NTFS_EA_GID`, and `NTFS_EA_MODE` are flags selecting which WSL EA metadata fields to write.
- `ntfs_xattr_handlers` is exported for superblock xattr handler registration.
- WSL EA helpers:
  - `ntfs_ea_set_wsl_not_symlink()`
  - `ntfs_ea_get_wsl_inode()`
  - `ntfs_ea_set_wsl_inode()`
- `ntfs_listxattr()` is declared for inode operation tables.
- With POSIX ACL support, the header declares `ntfs_get_acl()`, `ntfs_set_acl()`, and `ntfs_init_acl()`.
- Without POSIX ACL support, `ntfs_get_acl` and `ntfs_set_acl` are defined as `NULL` so inode operation tables can be initialized unconditionally.

## Dependencies And Invariants

This header depends on VFS inode, dentry, xattr, and POSIX ACL types through includers. The flag values are bit masks, not NTFS on-disk constants, and are interpreted only by the NTFS WSL EA helper routines.
