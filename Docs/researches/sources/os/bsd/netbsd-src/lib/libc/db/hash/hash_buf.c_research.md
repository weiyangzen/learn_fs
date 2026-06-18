# File Research: sources/os/bsd/netbsd-src/lib/libc/db/hash/hash_buf.c

Implements the hash access method's buffer cache. `__buf_init` initializes an LRU sentinel and computes the number of buffers allowed from the requested cache size. `__get_buf` returns a buffer for a bucket or overflow page, checking directory entries or previous-page overflow links, allocating or evicting as needed, reading page contents through `__get_page`, and moving hits to MRU position.

`newbuf` either allocates a new `BUFHEAD` and page buffer, or evicts the LRU unpinned buffer. Eviction writes dirty pages with `__put_page`, invalidates bucket directory entries, and flushes linked overflow buffers associated with the bucket. `__buf_free` writes dirty buffers on sync/close and optionally frees all buffers. `__reclaim_buf` resets a freed overflow buffer and moves it to the LRU end.

Dependencies include `hash.h` buffer flags and pointer tagging, `hash_page.c` page I/O, and directory/segment state in `HTAB`.

Risks/invariants: pinned buffers force allocation beyond the nominal cache size. Overflow-link cache pointers can become stale, so `__get_buf` validates addresses before reuse.
