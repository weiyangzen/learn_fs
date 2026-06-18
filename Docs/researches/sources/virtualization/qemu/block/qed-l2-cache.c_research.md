# File Research: sources/virtualization/qemu/block/qed-l2-cache.c

Implements QED's in-memory L2 table cache. The cache is a QTAILQ of `CachedL2Table` entries with reference counts, intended to avoid repeated image reads for recently used L2 tables while allowing in-flight requests to keep evicted tables alive.

`qed_alloc_l2_cache_entry()` creates an uninitialized refcounted entry. `qed_unref_l2_cache_entry()` drops a reference and frees the table with `qemu_vfree()` when the count reaches zero. `qed_find_l2_cache_entry()` searches by table file offset and increments the refcount on hits.

`qed_commit_l2_cache_entry()` inserts a freshly loaded or allocated L2 table after it is valid on disk and referenced by L1. If another request already committed the same offset, the new entry is discarded. The cache target is 50 entries; unused entries are evicted when possible, but the cache may temporarily grow if all entries are still referenced by active requests.
