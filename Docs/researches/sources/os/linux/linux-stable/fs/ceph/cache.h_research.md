# File Research: sources/os/linux/linux-stable/fs/ceph/cache.h

## Purpose

`cache.h` provides the CephFS FS-Cache interface, with real declarations and inline helpers when `CONFIG_CEPH_FSCACHE` is enabled and no-op fallbacks otherwise.

## Main Responsibilities

- Exposes mount-level and inode-level FS-Cache lifecycle functions.
- Provides `ceph_fscache_cookie()` accessor over `netfs_i_cookie()`.
- Provides cache resize, writeback unpin, dirty-folio, and cache-enabled helpers.
- Keeps the rest of CephFS code buildable without FS-Cache support.

## Enabled Build Behavior

When `CONFIG_CEPH_FSCACHE` is set:
- Real functions from `cache.c` are declared.
- `ceph_fscache_resize()` wraps `fscache_resize_cookie()` with use/unuse.
- `ceph_fscache_unpin_writeback()` delegates to `netfs_unpin_writeback()`.
- `ceph_fscache_dirty_folio` maps to `netfs_dirty_folio`.
- `ceph_is_cache_enabled()` checks `fscache_cookie_enabled()`.

## Disabled Build Behavior

When FS-Cache is disabled:
- Register/unregister/use/update/invalidate functions are inline no-ops.
- `ceph_fscache_cookie()` returns `NULL`.
- `ceph_fscache_unpin_writeback()` returns success.
- `ceph_fscache_dirty_folio` maps to `filemap_dirty_folio`.
- `ceph_is_cache_enabled()` returns false.

## Dependencies

- Linux netfs support.
- Linux FS-Cache support when enabled.
- Ceph inode structures through `struct ceph_inode_info`.
