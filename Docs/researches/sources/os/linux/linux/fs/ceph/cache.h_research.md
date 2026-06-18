# File Research: sources/os/linux/linux/fs/ceph/cache.h

## Purpose
Declares Ceph FS-Cache helpers and provides no-op fallbacks when `CONFIG_CEPH_FSCACHE` is disabled.

## Main Interfaces
When FS-Cache is enabled:
- `ceph_fscache_register_fs()`
- `ceph_fscache_unregister_fs()`
- `ceph_fscache_register_inode_cookie()`
- `ceph_fscache_unregister_inode_cookie()`
- `ceph_fscache_use_cookie()`
- `ceph_fscache_unuse_cookie()`
- `ceph_fscache_update()`
- `ceph_fscache_invalidate()`
- `ceph_fscache_cookie()`
- `ceph_fscache_resize()`
- `ceph_fscache_unpin_writeback()`
- `ceph_is_cache_enabled()`

## Conditional Behavior
- With `CONFIG_CEPH_FSCACHE`, helpers call Linux fscache/netfs APIs and `ceph_fscache_dirty_folio` aliases to `netfs_dirty_folio`.
- Without `CONFIG_CEPH_FSCACHE`, all helpers are no-ops or return false/zero/null, and `ceph_fscache_dirty_folio` aliases to `filemap_dirty_folio`.

## Integration
- Included by Ceph address-space and cap code to keep cache-aware paths buildable with and without FS-Cache.
- Uses `netfs_i_cookie(&ci->netfs)` to access the cookie.

## Risk Notes
- The fallback macros change dirty-folio behavior, so call sites must not assume FS-Cache state exists.
- `ceph_fscache_resize()` temporarily uses the cookie with `will_modify=true`; incorrect use/unuse pairing would affect cache coherency.
