# sources/user-network-fs/rclone/lib/cache/cache_test.go

## Purpose
This file tests the cache package's creation, negative caching, expiry, pinning, deletion, rename, and finalization semantics.

## Important APIs, types, and functions
- `setup(t)` builds a fresh `Cache` and a `CreateFunc` with deterministic responses for root, file, and error paths.
- Tests include `TestGet`, `TestGetFile`, `TestGetError`, `TestPutErr`, `TestPut`, `TestCacheExpire`, `TestCacheNoExpire`, `TestCachePin`, `TestClear`, `TestEntries`, `TestGetMaybe`, `TestDelete`, `TestDeletePrefix`, `TestCacheRename`, and `TestCacheFinalize`.

## Control flow
Most tests create a cache, perform one or more public operations, and inspect either public counts or internal map state under lock. Expiry tests shorten intervals and mutate `lastUsed` to avoid waiting for default durations. Finalizer tests install a counting finalizer and exercise every removal path.

## State and persistence behavior
Tests use package-level `called` and sentinel errors to assert create-call behavior. Cache state is in memory only. Some tests directly inspect or mutate private fields because they are in package `cache`, not `cache_test`.

## Dependencies and integration points
The tests use `testing`, `time`, `errors`, `fmt`, and `testify` assertions. They are direct unit tests for `cache.go` and do not require remote services.

## Risks and edge cases
`TestCacheExpire` uses real timers and sleeps, so it can be timing-sensitive on overloaded CI. The tests do not cover concurrent access or duplicate create races. They also do not check finalizer reentrancy or negative pin counts.

## Test signals
The suite is a strong signal for the documented single-threaded semantics: errors cache only when requested, disabled caches keep nothing, pinned stale entries survive expiry, prefix deletion counts exact matches, rename prefers existing destination values, and all removal paths call finalizers.
