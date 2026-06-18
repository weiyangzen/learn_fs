# File Research: sources/os/linux/linux/fs/netfs/fscache_io.c

Implements FS-Cache data I/O operation setup, cache writes, and resize operations.

Key responsibilities:
- Waits for cookie state to become usable for I/O.
- Begins read/write cache operations and attaches backend resources to `netfs_cache_resources`.
- Writes pagecache xarray ranges into cache storage.
- Clears deprecated `PG_private_2` bookkeeping bits after cache writes.
- Resizes backing cache objects synchronously under netfs inode serialization.

Important exported APIs:
- `fscache_wait_for_operation()`: waits until cookie reaches a state suitable for requested operation.
- `__fscache_begin_read_operation()`.
- `__fscache_begin_write_operation()`.
- `__fscache_clear_page_bits()`.
- `__fscache_write_to_cache()`.
- `__fscache_resize_cookie()`.

Important behavior:
- `fscache_begin_operation()` pins cookie access, stores debug/invalidation counters, waits through lookup/creation/invalidation/LRU-discard states, then calls backend `begin_operation`.
- Failed or non-live cookies return `-ENOBUFS` and drop the access pin.
- Cache writes allocate `struct fscache_write_request`, prepare the write through backend ops, build an xarray iterator over `mapping->i_pages`, then issue `fscache_write()`.
- Completion calls optional netfs termination callback, ends cache operation, clears `PG_private_2` if requested, and frees request state.
- Resizes are not deferred because they must be serialized inside the netfs inode lock.

Dependencies:
- FS-Cache cookie state machine.
- Backend cache `ops`: `begin_operation`, `prepare_write`, `resize_cookie`.
- Netfs cache resource helpers from public headers.
