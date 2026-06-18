# sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_VFS/vfs/attrs.c

Purpose: this file implements VFS sub-FSAL attribute hooks, especially referrals and optional ACL support.

Important functions: `vfs_sub_getattrs_common` populates `ATTR4_FS_LOCATIONS` for referral directories via `vfs_get_fs_locations`. `vfs_sub_getattrs_release` releases an existing ACL in an attrlist. Under `ENABLE_VFS_DEBUG_ACL`, an AVL-backed in-memory ACL store is implemented with `vfs_acl_init`, `vfs_acl_release`, `vfs_sub_getattrs`, and `vfs_sub_setattrs`. Under `ENABLE_VFS_POSIX_ACL`, `vfs_sub_getattrs` reads effective/default POSIX ACLs, converts them to FSAL ACLs, and sets `ATTR_ACL`; `vfs_sub_setattrs` converts FSAL ACLs back to POSIX access/default ACLs and writes them by fd. With neither option, getattrs only handles referrals and setattrs is a no-op.

Control flow and state: referral handling is common across all builds. Debug ACL mode stores ACLs in a process-global AVL keyed by object handle bytes. POSIX ACL mode reads/writes kernel ACL state on the object fd and skips object types where fd ACL access is invalid. `vfs_setattr2` and `fetch_attrs` call these hooks from file operations.

Dependencies and integration points: uses FSAL access/ACL conversion helpers, NFSv4 ACL intern/refcount helpers, POSIX ACL APIs when enabled, and `subfsal_helpers.c` for referrals.

Risks: debug ACL storage is not persistent and appears unprotected by explicit locks. POSIX ACL conversion doubles initial ACE allocation then shrinks after conversion; conversion errors must not leak ACL memory. `acl_set_fd` error mapping uses `fsalstat(errno, 0)` in some paths instead of `posix2fsal_error`, which should be verified. Referral getattrs passes `fd == -1` in some paths and POSIX ACL mode deliberately skips ACL reads for that case.

Test signals: referral fs_locations with/without ACLs, debug ACL get/set/release, POSIX ACL read/write on files and directories, default ACLs on directories, symlink/device/socket skip behavior, no-ACL builds, and attrlist ACL release/refcount correctness.
