# File Research: sources/os/linux/linux-stable/fs/9p/acl.h
- Purpose: Declares 9P ACL interfaces and provides disabled-config fallbacks.
- Main exports: ACL get/set inode operations, `v9fs_get_acl`, `v9fs_acl_chmod`, `v9fs_set_create_acl`, `v9fs_put_acl`, and `v9fs_acl_mode`.
- Conditional behavior: Under `CONFIG_9P_FS_POSIX_ACL`, real functions are declared. Without it, inode operation pointers are `NULL` and helpers return success/no ACL work.
- Integration: Used by inode creation, chmod, superblock xattr setup, and dotl/non-dotl inode operation tables.
- Research notes: This header is the compile-time compatibility layer that keeps 9P buildable without ACL support.
