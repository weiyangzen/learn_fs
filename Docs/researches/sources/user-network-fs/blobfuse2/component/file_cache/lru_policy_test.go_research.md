# sources/user-network-fs/blobfuse2/component/file_cache/lru_policy_test.go

Purpose: focused suite for the `lruPolicy` implementation, isolating policy state transitions from the full file-cache component.

Important APIs/types/functions: `lruPolicyTestSuite` stores a `*lruPolicy` and assertions. `SetupTest` creates a fixed `cache_path` under the home directory and starts a policy with timeout zero, default eviction count, thresholds, and a fresh `common.LockMap`. `setupTestHelper` starts a new policy for supplied `cachePolicyConfig`; `cleanupTest` shuts it down and removes the cache path. Test methods cover default values, `UpdateConfig`, `CacheValid`, `CacheInvalidate`, `CachePurge`, `IsCached`, timeout cleanup, and eviction count scenarios.

Control flow: tests construct a policy, invoke policy methods directly, and inspect `nodeMap` entries or `IsCached` results. Positive-timeout tests stop the default policy, restart with `cacheTimeout=1`, call `CacheValid`/`CacheInvalidate`, sleep five seconds, and expect expired entries to become uncached. The max-eviction tests add many names and rely on repeated timeout processing to remove all entries.

State and persistence behavior: most assertions inspect in-memory state (`nodeMap`, `lruNode.name`, `usage`, and cache timeout fields). `TestCacheInvalidate` creates a local file so the asynchronous delete path has a real target. Cleanup removes the shared cache directory after shutting down policy goroutines. The suite validates that `UpdateConfig` changes size/threshold/eviction/trace fields but intentionally does not change `cacheTimeout`.

Dependencies/integration points: depends on `common.LockMap`, filesystem directory creation/removal, `testify/suite`, the LRU policy implementation, default constants from file-cache configuration, and real time through `time.Sleep`.

Risks: the suite uses a fixed home-directory path (`file_cache`) rather than a randomized temp directory, so parallel runs or stale state can collide. Timeout tests sleep fixed five-second windows and can be flaky or slow. Max-eviction tests only assert eventual absence through `IsCached`; they do not inspect physical file deletion, disk-threshold eviction, lock-protected deletion, or marker list structure.

Test signals: confirms the primary public contract: default LRU identity/config, config update exclusions, valid entries become cached, zero timeout invalidates immediately, positive timeout retains until ticker expiry, purge removes map entries, cache lookup reflects map state, and large batches expire within the configured timeout.
