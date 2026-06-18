# File Research: sources/os/linux/linux-stable/fs/netfs/fscache_io.c

Implements cache data I/O entry points around FS-Cache cookies.

Key behavior:
- `fscache_begin_operation()` pins a cookie, waits through lookup/invalidation/creation states, and asks backend `begin_operation()` for operation resources.
- Read and write begin helpers select `FSCACHE_WANT_PARAMS`; write-to-cache uses `FSCACHE_WANT_WRITE`.
- `fscache_wait_for_operation()` waits until a cookie reaches an acceptable state and lazily begins a backend operation.
- `__fscache_write_to_cache()` builds an xarray iterator over pagecache data and dispatches backend cache writes with completion cleanup.
- Handles deprecated `PG_private_2` page-bit clearing for cache-copy completion.
- `__fscache_resize_cookie()` synchronously resizes backend cache objects under the caller’s inode serialization.

Important failure mode:
- If the cookie becomes not-live, dropped, or backend `begin_operation()` fails, the operation returns `-ENOBUFS` and unpins cookie access.
