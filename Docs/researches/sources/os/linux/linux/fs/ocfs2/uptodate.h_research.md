# File Research: sources/os/linux/linux/fs/ocfs2/uptodate.h

## Purpose

`uptodate.h` declares the OCFS2 clustered metadata uptodate cache interface and the callback operations required from cache owners.

## Key Type

`struct ocfs2_caching_operations` supplies:

- `co_owner()`: returns a `u64` owner identifier, usually a block number.
- `co_get_super()`: returns the relevant superblock for block/cluster conversion.
- `co_cache_lock()` / `co_cache_unlock()`: non-sleeping cache lock hooks.
- `co_io_lock()` / `co_io_unlock()`: sleeping I/O serialization hooks.

These callbacks let the generic cache code work for different OCFS2 owners while relying on owner-specific locking.

## API Surface

- `init_ocfs2_uptodate_cache()`
- `exit_ocfs2_uptodate_cache()`
- `ocfs2_metadata_cache_init()`
- `ocfs2_metadata_cache_purge()`
- `ocfs2_metadata_cache_exit()`
- `ocfs2_metadata_cache_owner()`
- `ocfs2_metadata_cache_io_lock()`
- `ocfs2_metadata_cache_io_unlock()`
- `ocfs2_buffer_uptodate()`
- `ocfs2_set_buffer_uptodate()`
- `ocfs2_set_new_buffer_uptodate()`
- `ocfs2_remove_from_cache()`
- `ocfs2_remove_xattr_clusters_from_cache()`
- `ocfs2_buffer_read_ahead()`

## Correctness Notes

- The header makes explicit that locking is provided by the cache owner, not by the generic type itself.
- Cache-lock callbacks must not sleep; I/O-lock callbacks may sleep.
- This separation is central to safe cache checks under buffer locks while still serializing I/O submitters.
