# File Research: sources/os/linux/linux/fs/ceph/cache.c

## Purpose
Implements CephFS FS-Cache volume and inode cookie registration helpers when `CONFIG_CEPH_FSCACHE` is enabled.

## Main Responsibilities
- Registers per-inode cache cookies for regular, newly created inodes.
- Registers and unregisters a filesystem-level FS-Cache volume.
- Provides wrappers for cookie use/unuse, update, and invalidation.

## Key Functions
- `ceph_fscache_register_inode_cookie()`:
  - exits when filesystem caching is disabled;
  - only supports regular files;
  - only registers cookies while inode is `I_NEW`;
  - uses `ci->i_vino` as the key and `ci->i_version` as coherency data;
  - sets `mapping_set_release_always()` when a cookie is acquired.
- `ceph_fscache_unregister_inode_cookie()` relinquishes the inode cookie.
- `ceph_fscache_use_cookie()` and `ceph_fscache_unuse_cookie()` wrap fscache pin/unpin. The update path supplies current version and size.
- `ceph_fscache_update()` updates cookie coherency data.
- `ceph_fscache_invalidate()` invalidates the cookie, using `FSCACHE_INVAL_DIO_WRITE` for direct-I/O write invalidations.
- `ceph_fscache_register_fs()` creates a volume name from Ceph fsid and optional `fscache_uniq`, acquires the FS-Cache volume, and reports mount-context errors.
- `ceph_fscache_unregister_fs()` relinquishes the volume.

## Integration
- Used by `addr.c` for dirty folio handling, read/write cache interaction, writeback unpinning, and invalidation during cap revocation.
- Stores the cookie in the embedded `netfs_inode` inside `ceph_inode_info`.

## Risk Notes
- Inode cookies are intentionally only registered for `I_NEW` regular files; late registration is avoided.
- Coherency depends on correct updates of `ci->i_version` and file size.
- Failure to acquire a volume disables caching by clearing `fsc->fscache`.
