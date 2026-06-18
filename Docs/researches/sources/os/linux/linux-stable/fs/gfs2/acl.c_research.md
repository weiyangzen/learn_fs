# File Research: sources/os/linux/linux-stable/fs/gfs2/acl.c

## Purpose
Implements GFS2 POSIX ACL get/set operations backed by system extended attributes.

## Key Interfaces
- `gfs2_get_acl()` retrieves ACLs under the inode glock.
- `__gfs2_set_acl()` serializes ACLs and writes system xattrs.
- `gfs2_set_acl()` is the VFS set-ACL entry point with quota and mode update handling.

## Control Flow And Behavior
ACL names are mapped from access/default ACL types to POSIX ACL xattr names. Gets reject RCU mode with `-ECHILD` and acquire a shared glock when needed. Sets enforce maximum ACL entry count, acquire quota data, take the inode glock exclusive when needed, update mode for access ACLs, write the xattr, update cached ACLs, and mark mode/ctime dirty when mode changes.

## Dependencies
Uses GFS2 xattr helpers, glocks, quota accounting, POSIX ACL conversion helpers, and inode dirtying.

## Risks And Invariants
ACL xattr access requires proper glock protection outside RCU lookup. Entry count is capped by block-size-derived `GFS2_ACL_MAX_ENTRIES`.
