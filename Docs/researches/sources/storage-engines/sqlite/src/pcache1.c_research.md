# sources/storage-engines/sqlite/src/pcache1.c

## Purpose

`pcache1.c` implements SQLite's default `sqlite3_pcache_methods2` backend. It provides page lookup by page number, page memory allocation and recycling, LRU management for unpinned pages, cache grouping for shared memory pressure, configured pagecache-buffer support, local bulk allocation, heap fallback, and optional memory release for `sqlite3_release_memory()`.

This layer does not know about pager dirty semantics beyond pinned versus unpinned page objects. It stores page content and backend headers in cache lines and gives `pcache.c` raw `sqlite3_pcache_page` handles. The file also installs itself through `sqlite3PCacheSetDefault()` when no application-defined cache backend is configured.

## Important Types and Functions

`PgHdr1` is the backend header and begins with `sqlite3_pcache_page` so it can be cast to the public backend page type. It stores `iKey`, bulk/local flags, hash-chain linkage, owning `PCache1`, and LRU links. A page is pinned when it is not on the LRU list.

`PGroup` groups one or more `PCache1` objects that can recycle each other's unpinned pages. It tracks shared limits (`nMaxPage`, `nMinPage`, `mxPinned`), total purgeable pages, an optional mutex, and a circular LRU anchor. Depending on configuration, each cache has a separate group or all caches share the global group.

`PCache1` stores page size, extra size, allocation size, purgeability, per-cache limits (`nMin`, `nMax`, `n90pct`), largest key, hash table state, count of recyclable and total pages, local free list, and local bulk allocation. `PCacheGlobal` stores global configured pagecache slots, free-slot list, pressure state, mutexes, and default group.

Allocation helpers include `sqlite3PCacheBufferSetup()`, `pcache1InitBulk()`, `pcache1Alloc()`, `pcache1Free()`, `pcache1AllocPage()`, `pcache1FreePage()`, `sqlite3PageMalloc()`, and `sqlite3PageFree()`. Cache helpers include `pcache1UnderMemoryPressure()`, `pcache1ResizeHash()`, `pcache1PinPage()`, `pcache1RemoveFromHash()`, `pcache1EnforceMaxPage()`, and `pcache1TruncateUnsafe()`.

The pluggable method implementations are `pcache1Init()`, `pcache1Shutdown()`, `pcache1Create()`, `pcache1Cachesize()`, `pcache1Shrink()`, `pcache1Pagecount()`, `pcache1Fetch()`, `pcache1Unpin()`, `pcache1Rekey()`, `pcache1Truncate()`, and `pcache1Destroy()`.

## Control Flow

Initialization zeroes global state, decides whether to use separate per-cache groups or one global group, allocates static mutexes when needed, and records local bulk-allocation policy. `pcache1Create()` allocates a cache plus optional per-cache group, initializes the LRU anchor, sets sizes, allocates a hash table, and contributes minimum page reservations for purgeable caches.

Fetch first searches the hash table. If found and unpinned, it is removed from LRU and returned pinned. If not found and `createFlag` is 0, fetch returns null. If `createFlag` is 1, `pcache1FetchStage2()` refuses allocation when too many pages are pinned or memory pressure is high. Otherwise it resizes the hash table when needed, tries to recycle the oldest unpinned LRU page if size and pressure rules allow, then allocates from local bulk memory, configured pagecache slots, or heap fallback. New pages are inserted into the hash table, marked pinned, and have their `pExtra` first pointer cleared so the upper layer can detect uninitialized `PgHdr`.

Unpin either frees the page immediately when reuse is unlikely or group limits are exceeded, or inserts it at the front of the circular LRU list. Rekey removes a page from its old hash bucket and inserts it under the new key. Truncate scans relevant hash buckets or the whole hash table to remove pages at or above a limit, pinning them first if they are on LRU. Destroy truncates all pages, updates group limits, frees bulk memory, hash table, and cache object.

## State and Persistence Behavior

The backend state is memory-residency state rather than disk persistence. Pinned pages are in active use by upper layers and cannot be recycled. Unpinned pages are candidates for reuse and are ordered in the group LRU. Purgeable caches count against group page limits and can donate pages to other caches in the same group. Non-purgeable caches, such as in-memory databases, do not use createFlag 1 and do not participate in the same purgeable accounting.

Page memory can come from three places: the general allocator, the global `SQLITE_CONFIG_PAGECACHE` buffer, or per-cache local bulk allocation. The configured pagecache pool tracks `nFreeSlot`, `nReserve`, and an atomic under-pressure flag. Local bulk allocation is initialized lazily on the first page allocation for a cache and is freed when the cache becomes empty.

## Dependencies and Integration Points

`pcache1.c` depends on SQLite memory allocation, mutex, status, atomic, and configuration APIs. It implements the `sqlite3_pcache_methods2` interface consumed by `pcache.c`. `sqlite3PCacheBufferSetup()` integrates startup configuration, `sqlite3PageMalloc()` and `sqlite3PageFree()` expose pagecache allocation for related SQLite internals, `sqlite3Pcache1Mutex()` supports status reporting, and optional `sqlite3PcacheReleaseMemory()` supports global memory pressure relief.

## Risks and Edge Cases

Hash table resizing releases and reacquires the group mutex around allocation, so callers must tolerate concurrent state changes under supported modes. Recycled pages must match allocation size; otherwise they are freed and a new allocation is attempted. LRU anchor handling depends on `isAnchor` and circular links being correct. `pcache1TruncateUnsafe()` has an optimized partial scan that depends on `iMaxKey` and hash modulo behavior. Global configured pagecache memory and local bulk memory are mutually exclusive in practice for initial bulk use, and pressure decisions must avoid overusing heap when a pagecache pool was expected to be sufficient.

The page layout intentionally places the backend header after page content so small btree overreads on corrupt databases land in initialized header memory. Structure padding choices and initialization are therefore correctness and tooling concerns, not only performance details.

## Test Signals

Tests should cover configured pagecache pools, heap fallback and overflow stats, local bulk allocation sizing, separate versus global group modes, hash lookup and resize, fetch createFlag 0/1/2 behavior, memory-pressure refusals, LRU recycling across caches, unpin with and without `reuseUnlikely`, rekey collision cases, truncate of pinned and unpinned pages, destroy after live pages have been truncated, `sqlite3_release_memory()` builds, status counters, and valgrind/ASAN runs against corrupt-page overread scenarios.
