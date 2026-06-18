# File Research: sources/os/linux/linux-stable/fs/xfs/xfs_acl.c

## Purpose

Implements POSIX ACL support for XFS by translating between Linux `struct posix_acl` objects and XFS on-disk ACL extended attributes.

## Main Responsibilities

- Converts on-disk ACL blobs to incore POSIX ACLs:
  - validates size/count
  - checks maximum entry limits
  - converts endian fields
  - maps user/group ids through `init_user_ns`
- Converts POSIX ACLs back to XFS disk format.
- Reads ACLs from root namespace xattrs:
  - `SGI_ACL_FILE`
  - `SGI_ACL_DEFAULT`
- Sets/removes ACL xattrs through `xfs_attr_change`.
- Updates cached ACL state after successful changes.
- Updates inode mode after successful access ACL updates.

## Important Behavior

`xfs_set_acl` updates the ACL xattr first and only changes `i_mode` afterwards. This avoids changing inode mode if the xattr update fails, for example due to `ENOSPC`.

Default ACLs are only valid for directories. Removing a nonexistent ACL is treated as success.

## Dependencies

- XFS attr layer for storage.
- Linux POSIX ACL helpers for validation and mode adjustment.
- XFS transaction layer for the separate mode update transaction.

## Risks

The ACL cache is invalidated by name through `xfs_forget_acl` when users bypass ACL helpers via xattr interfaces. The caller is then responsible for xattr content validity and mode consistency.
