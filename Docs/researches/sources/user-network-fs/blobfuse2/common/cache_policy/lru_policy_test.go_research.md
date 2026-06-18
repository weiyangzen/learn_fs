# sources/user-network-fs/blobfuse2/common/cache_policy/lru_policy_test.go
## sources/user-network-fs/blobfuse2/common/cache_policy/lru_policy_test.go

Purpose: unit tests for the `LRUCache` behavior in `lru_policy.go`.

Important APIs/helpers: `typesTestSuite`, `assertBlockCached`, `assertBlockNotCached`, and tests for construction, put, purge, not-found, resize, ordering, eviction, and dirty-block eviction.

Control flow: tests create small `common.Block` instances with start/end index ranges, insert them into caches of limited capacity, call `Get` to update recency, and assert `RecentlyUsed`, `LeastRecentlyUsed`, `Keys`, and `Occupied`. Dirty-block tests set and clear `common.DirtyBlock` flags to verify `Put` refuses insertion when all candidates are dirty, then evicts the clean candidate after flags are cleared.

State and persistence: tests are in-memory only. They mutate `Block.Flags` and cache internals but do not touch filesystem or external services.

Dependencies/integration: depends on `common.Block`, `common.BitMap64`, and testify suite/assert.

Risks: the suite does not exercise cache-level concurrent access despite `LRUCache` embedding `sync.RWMutex`. It does not cover duplicate keys, empty `RecentlyUsed`/`LeastRecentlyUsed`, oversized single-block insertion beyond capacity, or nil block values. Test suite type is named `typesTestSuite`, which can be confusing in the cache package.

Test signals: strong behavioral signal for current eviction policy: capacity is a trigger threshold, not a hard post-insertion limit, and dirty blocks are protected from eviction.
