# File Research: sources/os/bsd/netbsd-src/lib/libc/db/mpool/mpool.c

Implements the generic fixed-size page cache used by btree and recno. `mpool_open` validates a regular file, initializes LRU and hash queues, records page size, max cache, file descriptor, and current file page count. `mpool_filter` installs optional page-in/page-out byte-order or transformation callbacks.

`mpool_newf`/`mpool_new` allocate a new page number or requested page, acquire a cache bucket, mark it pinned/in-use, and insert it into hash/LRU queues. `mpool_get` returns a pinned page from cache or disk, moving hits to MRU position and running `pgin` after reads. `mpool_put` unpins pages and marks them dirty. `mpool_delete` removes a pinned page from queues and frees it.

`mpool_sync` writes all dirty pages then `fsync`s. `mpool_close` frees cached pages and the pool. `mpool_bkt` allocates or evicts an unpinned bucket, flushing dirty victims with `mpool_write`. `mpool_write` runs `pgout`, writes by page number, then reruns `pgin` to restore the in-memory representation. `mpool_look` searches the page hash table.

Risks/invariants: callers must pair every pinned `mpool_get`/new with `mpool_put` or delete. If all buffers are pinned, the cache grows beyond `maxcache`. Offset multiplication is checked for overflow.
