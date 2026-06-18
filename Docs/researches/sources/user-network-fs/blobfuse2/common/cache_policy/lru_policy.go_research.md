# sources/user-network-fs/blobfuse2/common/cache_policy/lru_policy.go
## sources/user-network-fs/blobfuse2/common/cache_policy/lru_policy.go

Purpose: provides an LRU cache for `common.Block` objects used by block-oriented cache flows.

Important APIs/types/functions: `KeyPair`, `LRUCache`, `NewLRUCache`, `Get`, `Resize`, `Put`, `Keys`, `RecentlyUsed`, `LeastRecentlyUsed`, `Remove`, `Purge`, `getKeyPair`, and `evict`.

Control flow: `Put` evicts one clean least-recently-used block when `Occupied >= Capacity`, then pushes a new list element to the front and records its pointer in `Elements`. `Get` finds a block, moves it to the front, and returns it. `Resize` updates `EndIndex` and adjusts `Occupied` by the size delta. `Remove` locks the block, adjusts occupancy, clears data, deletes map entry, and removes the list node. `evict` walks from the back toward the front until it finds a non-dirty block; dirty blocks are skipped.

State and persistence: all state is in memory: doubly linked list, map, capacity, occupied byte count, and block mutation (`Data = nil`, flags consulted). The struct embeds `sync.RWMutex`, but exported methods do not acquire the cache-level lock.

Dependencies/integration: depends on `container/list`, `common.Block` and its `Dirty`/lock behavior, and `common/log` for `Print`.

Risks: the unusual list storage wraps a manually allocated `*list.Element` inside the list's element; callers must use `getKeyPair`. Cache-level concurrency is not actually protected despite the embedded mutex. `Put` only evicts before insertion and may allow `Occupied` to exceed `Capacity`, especially for large blocks. `RecentlyUsed`/`LeastRecentlyUsed` panic on empty cache.

Test signals: `lru_policy_test.go` covers construction, put/get, purge, resize, LRU ordering, clean eviction, and dirty-block eviction refusal/selection.
