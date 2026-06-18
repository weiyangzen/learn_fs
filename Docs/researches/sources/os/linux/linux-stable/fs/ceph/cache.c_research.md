# File Research: sources/os/linux/linux-stable/fs/ceph/cache.c

## Purpose

`cache.c` implements CephFS FS-Cache volume and inode-cookie lifecycle helpers. It is compiled when `CONFIG_CEPH_FSCACHE` is enabled and backs the declarations in `cache.h`.

## Main Responsibilities

- Registers an FS-Cache volume for a mounted Ceph filesystem.
- Registers per-inode cookies for new regular-file inodes.
- Updates, invalidates, uses, unuses, and relinquishes FS-Cache cookies.

## Key Functions

- `ceph_fscache_register_fs()` builds a volume name from Ceph FSID and optional `fscache_uniq`, then calls `fscache_acquire_volume()`.
- `ceph_fscache_unregister_fs()` relinquishes the volume.
- `ceph_fscache_register_inode_cookie()` acquires a cookie for new regular files only, using `i_vino` as key and `i_version` plus file size as coherency data.
- `ceph_fscache_unregister_inode_cookie()` relinquishes an inode cookie.
- `ceph_fscache_use_cookie()` and `ceph_fscache_unuse_cookie()` bracket cache usage, optionally updating coherency metadata.
- `ceph_fscache_update()` updates cookie coherency from inode version and size.
- `ceph_fscache_invalidate()` invalidates cached contents, marking direct-I/O write invalidations when applicable.

## Important Conditions

- No inode cookie is registered if the mount has no FS-Cache volume.
- Only regular files are cacheable.
- Only `I_NEW` inodes get cookies here.
- A successfully cached inode mapping is marked `mapping_set_release_always()` so release callbacks happen consistently.

## Dependencies

- `super.h` for Ceph inode/client accessors.
- Linux FS-Cache APIs.
- `cache.h` for exported declarations and inline wrappers.
- Used by `addr.c` writeback and invalidation paths.
