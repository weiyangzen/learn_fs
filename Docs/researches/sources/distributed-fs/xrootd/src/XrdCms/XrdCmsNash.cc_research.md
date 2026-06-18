# sources/distributed-fs/xrootd/src/XrdCms/XrdCmsNash.cc

Purpose: implements the physical hash table used by the CMS cache to map `XrdCmsKey` path keys to pooled `XrdCmsKeyItem` entries.

Important APIs/types/functions: constructor, `Add()`, `Expand()`, `Find()`, and `Recycle()`. `LoadMax` is 80 percent.

Control flow: construction allocates a zeroed table with a configured Fibonacci pair of previous/current sizes and threshold. `Add()` allocates a key item, expands if the load threshold is exceeded, ensures the key has a hash, copies the key into the item, and prepends it in the hash bucket. `Expand()` allocates a new table whose size is previous plus current, redistributes all items by saved hash modulo new size, frees the old table, and recomputes the threshold. `Find()` computes hash if needed and walks the bucket by key equality. `Recycle()` expects an unloaded item with its original hash in `Loc.HashSave`, unlinks it from the corresponding bucket, recycles the item, and decrements the count.

State and persistence behavior: process-local table only. Table size grows but does not shrink. Entries are owned by `XrdCmsKeyItem` pool.

Dependencies: `XrdCmsNash.hh`, `XrdCmsKey`, C allocation/memset/free.

Integration points: used by `XrdCmsCache` as the fast physical map. It relies on `XrdCmsKeyItem::Alloc()` and `Recycle()` semantics.

Risks: constructor does not check `malloc()` before `memset()`. `Add()` increments `nashnum` before expansion; if expansion allocation fails the table continues at a higher load. No locking. `Recycle()` depends on prior `Unload()` storing `HashSave`; using it on a normal item can search the wrong bucket.

Test signals: add/find with collisions, expansion redistribution, allocation-failure handling, recycle after unload, table load threshold behavior, and cache-level concurrency serialization.
