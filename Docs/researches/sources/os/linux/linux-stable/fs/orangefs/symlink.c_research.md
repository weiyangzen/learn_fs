# File Research: sources/os/linux/linux-stable/fs/orangefs/symlink.c

## Scope

This small file defines the inode operation table for OrangeFS symlinks.

## APIs And Constants

- Exports `orangefs_symlink_inode_operations`.

## Behavior

- Symlink bodies are served through `simple_get_link`, using the cached link target stored in the inode.
- Attribute changes, getattr, xattr listing, permission checks, and timestamp updates are routed to OrangeFS common handlers:
  - `orangefs_setattr`
  - `orangefs_getattr`
  - `orangefs_listxattr`
  - `orangefs_permission`
  - `orangefs_update_time`

## Dependencies

- Includes OrangeFS protocol, kernel, and buffer-map headers.
- Relies on `orangefs_inode_getattr()` initialization of `inode->i_link` for new symlink inodes.

## Risks And Invariants

- The symlink target must already be resident in OrangeFS private inode storage when `simple_get_link` is used.
- Symlink xattr get/set behavior is constrained in `xattr.c`; this table exposes only listxattr directly.
