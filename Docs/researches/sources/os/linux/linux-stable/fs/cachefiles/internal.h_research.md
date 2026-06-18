# File Research: sources/os/linux/linux-stable/fs/cachefiles/internal.h

This header defines CacheFiles internal data structures, enums, inline helpers, prototypes, error macros, and debug/assertion helpers.

Core data structures:
- `enum cachefiles_content`: persistent content states stored on disk, including no data, single/all data, backing-fs map, and dirty.
- `struct cachefiles_volume`: per-FS-Cache volume state with cache pointer, FS-Cache volume cookie, volume dentry, and 256 fanout dentries.
- `enum cachefiles_object_state` and `struct cachefiles_ondemand_info`: on-demand object state and worker/lock/id tracking.
- `struct cachefiles_object`: per-cookie object with FS-Cache cookie, volume, active-list link, backing file, cooked name, debug id, lock, refcount, content state, flags, and optional on-demand data.
- `struct cachefiles_cache`: whole cache state, including FS-Cache cookie, mount, store/graveyard dentries, daemon file, lists, credentials, daemon synchronization, release counters, threshold percentages and computed limits, flags, root/tag, unbind pin, on-demand xarrays, id counters, and security id state.
- `struct cachefiles_req`: on-demand request record with object pointer, completion, refcount, error, and user-visible message.

Important flags:
- Cache flags include ready, dead, culling, state changed, and on-demand mode.
- Object flag `CACHEFILES_OBJECT_USING_TMPFILE` tracks unlinked tmpfile storage.
- `CACHEFILES_REQ_NEW` is the xarray mark used to select unread on-demand requests.

Inline helpers:
- `cachefiles_in_ondemand_mode()`
- resource accessors for `netfs_cache_resources`
- daemon state wakeup helper
- optional error injection no-op implementations
- injected read/write/remove error helpers
- secure credential override begin/end helpers
- on-demand object state helpers and stubs when disabled.

Prototype organization:
- Grouped declarations for `cache.c`, `daemon.c`, `interface.c`, `io.c`, `key.c`, `namei.c`, `ondemand.c`, `security.c`, `volume.c`, and `xattr.c`.

Error handling:
- `cachefiles_io_error()` logs, notifies FS-Cache, marks the cache dead, and flushes on-demand requests when applicable.
- `cachefiles_io_error_obj()` adds object debug id context.

Debugging:
- Runtime debug masks are defined for function entry, exit, and debug messages.
- Assertions call `BUG()` in the active configuration block.
