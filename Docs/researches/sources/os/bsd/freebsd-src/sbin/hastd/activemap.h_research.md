# File Research: sources/os/bsd/freebsd-src/sbin/hastd/activemap.h

`activemap.h` declares the opaque activemap API used by HAST.

Key API groups:
- Lifecycle: `activemap_init()`, `activemap_free()`.
- Write tracking: `activemap_write_start()`, `activemap_write_complete()`, `activemap_extent_complete()`.
- Querying: `activemap_ndirty()`, `activemap_differ()`, `activemap_size()`, `activemap_ondisk_size()`.
- Bitmap I/O: `activemap_copyin()`, `activemap_merge()`, `activemap_bitmap()`, `activemap_calc_ondisk_size()`.
- Synchronization: `activemap_sync_rewind()`, `activemap_sync_offset()`, `activemap_need_sync()`.
- Diagnostic dump: `activemap_dump()`.

The header keeps `struct activemap` opaque to callers.
