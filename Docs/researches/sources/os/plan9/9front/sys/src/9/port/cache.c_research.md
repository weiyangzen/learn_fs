# File Research: sources/os/plan9/9front/sys/src/9/port/cache.c

Portable client-side file data cache for mount channels.

Key behavior:
- `cinit` preallocates a fixed set of `Mntcache` entries and creates the `fscache` image used for cached pages.
- Caches are keyed by channel type/dev/qid, tracked in a hash table and an LRU list.
- `Mntcache` has a recursive qlock because mount read-ahead can call cache update paths while already holding the cache lock.
- `copen` attaches or allocates a cache entry for non-directory channels, reusing entries by exact qid or qid ignoring version.
- `cread` reads contiguous valid cached page ranges, then falls back to mount read-ahead for misses.
- Cached page ranges are tracked per page through a bitmap and packed offset/end metadata in `Page.va`.
- `cupdate` and `cwrite` update cached data after reads/writes; writes bump qid versions and avoid caching append writes.
- `ctrunc` invalidates cached data and read-ahead state after truncation.
- `cclunk` resets read-ahead state and clears the channel’s cache pointer.

Notable dependencies:
- VM page cache/image primitives: `newimage`, `newpage`, `cachepage`, `lookpage`, `putpage`, `kmap`.
- Mount read-ahead helpers from `devmnt.c`.

Research notes:
- Cacheable range is capped at `MAXCACHE` per file.
- If memory pressure is detected while inserting pages, the code invalidates the remaining range rather than forcing cache population.
