# File Research: sources/os/linux/linux-stable/fs/ocfs2/acl.c

Purpose: Implements OCFS2 POSIX ACL conversion, get/set inode operations, chmod ACL updates, and new-inode ACL initialization.

Key responsibilities:
- Converts OCFS2 on-disk ACL xattr entries to/from Linux `struct posix_acl` with `ocfs2_acl_from_xattr()` and `ocfs2_acl_to_xattr()`.
- Reads ACL xattrs without taking inode cluster locks in `ocfs2_get_acl_nolock()`, using OCFS2 xattr indexes for access/default ACLs.
- Updates inode mode in memory and on disk through `ocfs2_acl_set_mode()`, optionally starting its own journal transaction and journaling dinode writes.
- Sets ACL xattrs with `ocfs2_set_acl()`, optionally using an existing journal handle and allocation contexts.
- Provides VFS inode operations `ocfs2_iop_get_acl()` and `ocfs2_iop_set_acl()`, taking OCFS2 inode locks and xattr semaphores as needed.
- Updates access ACL after chmod with `ocfs2_acl_chmod()`.
- Initializes ACLs for new inodes in `ocfs2_init_acl()`, inheriting a parent default ACL when present or applying current umask otherwise.

Important invariants:
- Symlinks do not support ACL mutation.
- Default ACLs apply only to directories; setting a default ACL on a non-directory returns `-EACCES` if one is supplied.
- `ocfs2_iop_get_acl()` refuses RCU mode with `-ECHILD`.
- ACL support is gated at runtime by `OCFS2_MOUNT_POSIX_ACL`.
- Mode updates must be journaled to the dinode and update ctime.
- Cached ACLs are updated after successful set operations.

Dependencies:
- Uses OCFS2 xattr APIs, inode locking, journaling, allocation contexts, dinode layout, and masklog error reporting.
- Uses generic POSIX ACL helpers for mode calculation, ACL creation, chmod, and xattr conversion semantics.

Risk notes:
- On-disk ACL entry count is `size / sizeof(struct posix_acl_entry)` without checking for trailing bytes, matching existing code but worth noting for validation expectations.
- `ocfs2_acl_set_mode()` may create and commit its own transaction when callers do not provide one, so callers must understand journaling context and lock state.
- Error paths log with `mlog_errno()` in some mode-update cases but not every ACL/xattr failure.
