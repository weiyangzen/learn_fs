# sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/blkid/cache.c

Purpose: owns allocation, initialization, cleanup, and garbage collection for libblkid caches.

Important APIs and control flow: `blkid_get_cache(ret_cache, filename)` allocates `struct blkid_struct_cache`, initializes device/tag list heads, chooses a cache filename from explicit argument, safe `BLKID_FILE`, or `/etc/blkid.tab`, duplicates it, then calls `blkid_read_cache`. `safe_getenv()` ignores environment variables for setuid/setgid or non-dumpable processes and uses `__secure_getenv` when available. `blkid_put_cache(cache)` flushes cache changes, frees devices, tag heads and dangling tags, filename, and cache. `blkid_gc_cache(cache)` stats each device path and removes missing devices.

State and persistence: owns in-memory cache lists and the cache filename; `blkid_flush_cache` persists changes on put or explicit flush.

Dependencies and integration: depends on `read.c`, `save.c`, `dev.c`, `tag.c`, safe environment behavior, and debug masks.

Risks and test signals: `blkid_get_cache` does not handle `blkid_strdup` failure explicitly, and cache operations are not synchronized. Test secure env suppression, missing cache files, GC deletion, flush-on-put, debug init, and memory cleanup.
