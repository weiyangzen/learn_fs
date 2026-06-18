<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/cache/metadata/type_cache_test.go -->
# Research: sources/user-network-fs/gcsfuse/internal/cache/metadata/type_cache_test.go

Purpose: unit-tests the metadata type cache implementation, including constructor modes, TTL semantics, overwrite behavior, LRU capacity eviction, explicit erase, reinsert, and disabled-cache behavior.

Important APIs/types/functions: `TestTypeCache`, suites `TypeCacheTest`, `ZeroSizeTypeCacheTest`, `ZeroTtlTypeCacheTest`, helper `createNewTypeCache`, constants `TTL` and `TypeCacheMaxSizeMB`, and fixed timestamps `now`, `expiration`, `beforeExpiration`, and `afterExpiration`.

Control flow: the primary suite creates a one-MiB cache with millisecond TTL, inserts named entries, and calls `Get` at controlled times. The capacity test computes how many entries of a known key size fit, inserts one more than capacity, then verifies that the first entry is evicted while later entries remain. Separate suites construct caches with zero max size and zero TTL and assert that inserts never become observable.

State and persistence: all test state is in-memory. The tests rely on deterministic caller-supplied timestamps instead of wall-clock sleeps, so expiration behavior is repeatable.

Dependencies and integration points: uses `internal/util.MiBsToBytes`, ogletest assertions, and direct access to unexported `typeCache` internals because the test package is `metadata`. It validates the cache behavior that filesystem directory type lookups rely on.

Risks: the size-eviction test is sensitive to `cacheEntry.Size` and key length. The tests do not cover concurrent access, matching the production contract that external synchronization is required. Constructor tests inspect `entries == nil`, so internal representation changes would require updates even if public behavior remains stable.

Test signals: coverage confirms entries are valid before TTL expiration, invalid after expiration, overwritten entries return the last type, erased entries vanish, and disabled caches always return `UnknownType`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/cache/metadata/type_cache_test.go -->
