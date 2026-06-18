# File Research: sources/os/linux/linux-stable/fs/xfs/xfs_handle.c

## Purpose

Implements XFS handle-based userspace operations: creating filesystem/file handles, opening or reading by handle, by-handle extended attribute operations, and parent-pointer enumeration.

## Main Responsibilities

- Formats filesystem and file handles:
  - fixed fsid from mount
  - inode number
  - inode generation
- Implements handle lookup ioctls:
  - path to filesystem handle
  - path to file handle
  - fd to file handle
- Converts handles back to dentries or inodes:
  - `xfs_handle_to_dentry`
  - `xfs_khandle_to_dentry`
  - `xfs_khandle_to_inode`
- Opens files by handle with admin permission and mode restrictions.
- Reads symlink target by handle.
- Lists xattrs with XFS attrlist format and cursor validation.
- Executes xattr multi-ops by handle:
  - get
  - set
  - remove
- Handles namespace filtering for root/secure/user xattrs.
- Forgets cached ACLs when root ACL attrs are changed.
- Implements parent pointer enumeration:
  - formats parent handles plus names into caller buffer
  - uses attr cursor continuation
  - marks corrupt parent pointer attrs sick
  - returns root and done flags
- Supports parent lookup by current file or by handle.

## Important Invariants

- Most handle operations require `CAP_SYS_ADMIN`.
- Handles are only generated for XFS regular files, directories, and symlinks.
- Open-by-handle is restricted to regular files and directories.
- Handle opens must be under a directory file.
- Write opens respect append-only, immutable, and directory restrictions.
- Attr namespace flags are mutually exclusive.
- Attr list cursor padding and initialization fields are validated.
- Parent pointer APIs require the parent-pointer feature.
- Parent record sizes are 64-bit aligned and the last record is expanded to fill the reported buffer region.

## Dependencies

- Uses exportfs decode and `xfs_nfs_get_inode` for handle resolution.
- Uses XFS attr, xattr, ACL, parent-pointer, health, and icache helpers.
- Uses VFS `dentry_open`, mount write guards, `vfs_readlink`, and usercopy helpers.

## Research Notes

This file is a privileged administrative interface for stable inode identity and metadata traversal. The parent-pointer code is newer and tightly integrated with xattr listing and health tracking.
