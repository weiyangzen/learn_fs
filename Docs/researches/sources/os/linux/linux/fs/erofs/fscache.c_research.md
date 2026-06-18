# File Research: sources/os/linux/linux/fs/erofs/fscache.c

Implements deprecated EROFS fscache/cachefiles on-demand read support.

Key behavior:
- Defines fscache I/O and request wrappers with refcounted completion.
- Reads cache data through `fscache_begin_read_operation()`, `prepare_ondemand_read()`, and `fscache_read()`.
- Provides bio allocation/submission wrappers for fscache-backed devices.
- Metadata read_folio reads from a fscache cookie-backed anonymous inode.
- Data reads map logical ranges, copy inline metadata, zero holes, or read mapped extents from the proper fscache cookie.
- Readahead drains folios from the readahead control and completes them through request completion.
- Manages shared fscache domains, volumes, cookies, and a pseudo mount for shareable anonymous blob inodes.
- Registers the primary filesystem blob cookie and unregisters cookies/domain/volume on teardown.
- Shared-domain mode enforces uniqueness for the primary fsid blob.

Important interactions:
- Used only when `CONFIG_EROFS_FS_ONDEMAND` and fscache mode are active.
- Multi-device mappings use per-device fscache cookies.
- Domain and cookie lists are protected by separate mutexes.
