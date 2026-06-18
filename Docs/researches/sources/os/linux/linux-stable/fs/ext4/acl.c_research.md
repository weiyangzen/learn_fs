# File Research: sources/os/linux/linux-stable/fs/ext4/acl.c

## Purpose

Implements ext4 POSIX ACL conversion, retrieval, setting, and new-inode ACL initialization.

## Main Responsibilities

- Converts ACL xattr bytes from disk format into `struct posix_acl`.
- Converts `struct posix_acl` back into ext4 on-disk ACL xattr format.
- Implements VFS ACL hooks `ext4_get_acl()` and `ext4_set_acl()`.
- Initializes inherited ACLs for newly created inodes via `ext4_init_acl()`.

## Key Operations

- `ext4_acl_from_disk()` validates ACL version, computes entry count, allocates a POSIX ACL, converts tags/perms/ids, and rejects malformed sizes or unknown tags.
- `ext4_acl_to_disk()` serializes POSIX ACL entries into the compact ext4 ACL format, using short entries for owner/group/mask/other and full entries for named users/groups.
- `ext4_get_acl()` chooses access/default ACL xattr namespace, fetches the xattr with `ext4_xattr_get()`, and converts it.
- `__ext4_set_acl()` serializes ACL data and stores it with `ext4_xattr_set_handle()` inside a journal transaction.
- `ext4_set_acl()` initializes quotas, computes xattr journal credits, starts a journal handle, updates inode mode for access ACLs through `posix_acl_update_mode()`, sets the xattr, marks inode dirty if mode changed, and retries on ENOSPC when appropriate.
- `ext4_init_acl()` uses `posix_acl_create()` to derive inherited default/access ACLs and creates corresponding xattrs on a new inode.

## Dependencies

- Includes quotaops, `ext4_jbd2.h`, `ext4.h`, `xattr.h`, and `acl.h`.
- Uses ext4 journaling, quota initialization, xattr credit calculation, inode dirtying, and allocation retry support.

## Research Notes

ACL changes are journaled metadata updates. The file carefully couples xattr mutation with inode mode updates, so POSIX mode bits and access ACL state remain consistent.
