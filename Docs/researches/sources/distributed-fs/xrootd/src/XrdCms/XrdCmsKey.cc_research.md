# sources/distributed-fs/xrootd/src/XrdCms/XrdCmsKey.cc

Purpose: implements hashing and pooled allocation/unload/recycle for CMS cache key items. These objects back `XrdCmsCache` and the `XrdCmsNash` hash table.

Important APIs/types/functions: `XrdCmsKey::setHash()`, `XrdCmsKeyItem::{Alloc,Recycle,Reload,Replenish,Stats,Unload}` and static state `TockTable`, `Free`, `numFree`, `numHave`, `numNull`.

Control flow: `setHash()` computes CRC32 over the key path and coerces zero to one. `Alloc()` pops a free item, stamps it into the current tick bucket, bumps the key reference byte away from zero, clears pending counters, and returns it; if the free list is empty, it repeatedly calls `Replenish()` to allocate `minAlloc` objects. `Recycle()` frees the key string, clears hash state, increments the ref byte, and pushes the item to `Free`. `Reload()` reinserts an existing item into its tick bucket. `Unload(tock)` removes a tick bucket, moves entries whose `TOD` changed to the correct bucket, and makes remaining entries unfindable by moving the hash into `Loc.HashSave`. `Unload(item)` removes one item from its tick chain and similarly saves/clears its hash.

State and persistence behavior: all state is process-memory cache state. Tick buckets provide time-based grouping for cache unload/recycle. Items are allocated in large arrays and normally never individually deleted.

Dependencies: `XrdOucCRC`, `XrdCmsTypes`, CMS tracing and error logging, C allocation/free.

Integration points: `XrdCmsNash::Add()` obtains items here, and `XrdCmsNash::Recycle()` expects `Unload()` to have saved the original hash in `Loc.HashSave`. `XrdCmsCache` uses key location fields for file/server presence and pending redirect state.

Risks: there is no internal locking in this file; callers must serialize access. `operator=` in the header duplicates `Val`, so `Recycle()` must own/free that memory. Tick/ref wraparound is mitigated by avoiding zero ref but still relies on cache discipline. `Unload()` temporarily clears hashes, so recycling without saved hashes breaks hash-table removal.

Test signals: hash determinism, zero-hash fallback, allocation after replenish, recycle string ownership, unload-by-tick bucket movement, unload-by-item hash save, stats reset of `numNull`, and concurrency tests at the cache layer.
