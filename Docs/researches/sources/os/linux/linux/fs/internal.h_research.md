# File Research: sources/os/linux/linux/fs/internal.h

Private VFS header shared among `fs/` implementation files. It declares internal functions and small helpers that should not be part of the public filesystem API.

Coverage:
- Block device, buffer, char device, fs context, namei, namespace, fs_struct, file table, superblock, open, inode, writeback, dcache, pipe, fs_pin, namespace fs, stat, splice, xattr, ACL, attr/idmap, anon inode, pidfs, and nsfs internal interfaces.
- Defines `struct open_flags`, xattr helper structs, stashed dentry operations, and `path_mounted()`.

Important inline helpers:
- `file_put_write_access()` and `put_file_access()` release inode and mount write/read accounting.
- `sb_start_ro_state_change()` and `sb_end_ro_state_change()` coordinate read-only remount state with memory barriers so `mnt_is_readonly()` observes consistent superblock state.

Role:
- This header is an integration map for VFS internals. Files such as `fs/init.c`, `fs/ioctl.c`, and `fs/inode.c` consume these declarations to call across fs implementation units without exposing symbols globally.

Risks:
- Declarations here encode private coupling. Signature changes must be coordinated with all implementation and call sites.
- The read-only remount helpers depend on paired barriers documented in comments; weakening them can break mount write-access correctness.
