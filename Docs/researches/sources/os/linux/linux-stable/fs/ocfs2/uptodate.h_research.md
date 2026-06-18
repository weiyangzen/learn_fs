# File Research: sources/os/linux/linux-stable/fs/ocfs2/uptodate.h

Declares OCFS2 metadata-cache operations for clustered uptodate tracking.

Key contents:
- Defines `struct ocfs2_caching_operations`, the callback table used by generic metadata-cache code to get the owner id, superblock, cache spinlock operations, and sleeping I/O lock operations.
- Declares slab lifecycle: `init_ocfs2_uptodate_cache()` and `exit_ocfs2_uptodate_cache()`.
- Declares cache lifecycle: `ocfs2_metadata_cache_init()`, `ocfs2_metadata_cache_purge()`, and `ocfs2_metadata_cache_exit()`.
- Declares owner/I/O helpers: `ocfs2_metadata_cache_owner()`, `ocfs2_metadata_cache_io_lock()`, and `ocfs2_metadata_cache_io_unlock()`.
- Declares buffer-state APIs: `ocfs2_buffer_uptodate()`, `ocfs2_set_buffer_uptodate()`, `ocfs2_set_new_buffer_uptodate()`, `ocfs2_remove_from_cache()`, `ocfs2_remove_xattr_clusters_from_cache()`, and `ocfs2_buffer_read_ahead()`.

Integration points:
- Included by inode initialization, buffer-head I/O, allocator, xattr, and metadata validation paths.
- Caching operation implementations connect this generic cache to inode or other metadata owners.

Risk areas:
- Callers must provide non-sleeping cache locks and sleeping I/O locks with the expected semantics.
- `ocfs2_buffer_uptodate()` is a cluster-coherency check, not just a wrapper around `buffer_uptodate()`.
- Removal APIs must be called when metadata blocks are freed or xattr clusters are removed to avoid trusting stale local buffers.
