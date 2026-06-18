# File Research: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/util/alloc.c

`alloc.c` implements libunbound’s per-thread allocation cache for two hot allocation classes: packed RRset keys (`alloc_special_type`) and reusable `regional` query-state arenas. A top-level allocator has a lock and serves as a shared super-cache; thread-local allocators can keep small local quarantines to reduce malloc/free and lock contention.

Special RRset allocation initializes embedded locks and key pointers, assigns per-thread 64-bit IDs, and recycles freed objects through local or super caches. IDs reserve high bits for the thread number and detect wraparound; on exhaustion, the configured cleanup callback is invoked to clear caches holding stale RRset IDs.

Regional allocation keeps up to ten custom 16 KiB regional arenas per allocator. Released arenas are reset with `regional_free_all()` and cached unless the per-allocator limit has been reached.

With `UNBOUND_ALLOC_STATS`, the file wraps malloc/calloc/free/realloc/strdup with accounting headers, a magic marker, and optional log-at-call-site wrappers. With `UNBOUND_ALLOC_LITE`, it adds front/back guard bytes, detects overwrite on free/realloc, fills allocated/freed memory with debug patterns, and wraps selected sldns/OpenSSL allocation-returning APIs so they use the lite allocator.
