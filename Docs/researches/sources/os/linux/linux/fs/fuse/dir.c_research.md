# File Research: sources/os/linux/linux/fs/fuse/dir.c

Purpose: Implements FUSE VFS directory, dentry, symlink, permission, lookup, creation, removal, rename, getattr/statx, setattr, and directory file operations.

Key responsibilities:
- Maintains FUSE dentry timeout state through `struct fuse_dentry`, per-bucket rbtree tracking, `inval_wq`, and `fuse_dentry_tree_work()`.
- Implements dentry operations: `fuse_dentry_revalidate()`, `fuse_dentry_delete()`, `fuse_dentry_init()`, `fuse_dentry_release()`, and automount setup for FUSE submounts.
- Converts FUSE lookup replies into inodes via `fuse_lookup_name()` and `fuse_iget()`, with FORGET handling on error.
- Implements create paths: `FUSE_CREATE`, fallback `mknod`, `mkdir`, `symlink`, `tmpfile`, and `link`.
- Builds optional create extensions for LSM security context and supplementary group propagation.
- Handles unlink/rmdir/rename cache invalidation, local link count updates, ctime updates, and interrupted-operation uncertainty.
- Implements `getattr` via `FUSE_GETATTR` and optional `FUSE_STATX`, including btime caching and fallback when `STATX` is unsupported.
- Implements permission model split between kernel-side `default_permissions` and server-side `FUSE_ACCESS`.
- Implements `FUSE_SETATTR`, including truncate synchronization through `FUSE_NOWRITE`, writeback-cache handling, DAX layout breakage, suid/sgid kill flags, and local cmtime trust rules.
- Provides directory open/release/fsync/ioctl and symlink readlink/page-cache support.

Important data/control flow:
- Dentry timeout is separate from inode attribute timeout. Dentry expiry causes lookup revalidation; inode expiry causes getattr/statx refresh.
- `fc->epoch` invalidates all dentries after connection-wide events; `fuse_epoch_work()` shrinks dcache under `fc->killsb`.
- `fuse_lock_inode()` serializes lookup/readdir unless `FUSE_PARALLEL_DIROPS` was negotiated.
- Attribute freshness is guarded by `fi->attr_version`, `fi->inval_mask`, `fi->i_time`, and writeback-cache-specific cache masks.
- `fuse_do_setattr()` is shared by directory and file paths and is a critical consistency point for truncation, ctime/mtime, page-cache invalidation, and DAX faults.

External dependencies:
- Core FUSE definitions from `fuse_i.h`.
- VFS dentry/inode/file APIs, idmapped mount helpers, ACL/security hooks, and folio/page-cache helpers.
- Request transport through `fuse_simple_request()` and `fuse_simple_idmap_request()`.

Notable edge cases:
- Zero nodeid in lookup is treated as negative lookup with valid timeout.
- Revalidation invalidates if nodeid, generation, type, or submount-flag identity changes.
- Interrupted unlink/rename invalidates affected dentries because userspace may already have completed the operation.
- Sticky bit is hidden from VFS permission checks when `default_permissions` is disabled, preserving server-controlled semantics.
