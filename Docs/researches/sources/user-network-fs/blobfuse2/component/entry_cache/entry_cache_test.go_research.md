# sources/user-network-fs/blobfuse2/component/entry_cache/entry_cache_test.go

## Purpose

`entry_cache_test.go` tests the `EntryCache` component against a loopback backend, focusing on caching, cache miss behavior, and TTL expiration.

## Important APIs, Types, and Functions

The suite defines `entryCacheTestSuite`, `newLoopbackFS`, `newEntryCache`, `randomString`, `setupTestHelper`, and `cleanupTest`. It exercises `EntryCache.Configure`, `Start`, `Stop`, and `StreamDir`.

## Control Flow

`SetupTest` creates a temporary loopback storage directory and configures `read-only: true` with a seven-second entry-cache timeout. Tests call `StreamDir` on empty, missing, and populated directories. One test creates an additional file after the initial listing, verifies that the cached listing still has the first result, sleeps long enough for eviction, and then verifies that a fresh listing sees both files.

## State and Persistence Behavior

The suite creates and removes temporary directories under the user's home directory. It inspects `entryCache.pathMap` directly for the `##` root key and relies on the TLRU expiration worker to remove entries.

## Dependencies and Integration Points

It depends on `loopback`, Blobfuse `config`, `log`, `common`, `internal`, `testify`, and filesystem operations. It validates that the cache composes with a real component rather than a mock.

## Risks and Edge Cases

`TestCachedEntry` sleeps 40 seconds for a seven-second timeout, making the suite slow. The direct `pathMap` inspection couples tests to internal key formatting. The tests do not cover paginated non-empty tokens beyond the root empty token key.

## Test Signals

Passing tests show that non-empty listings are cached, empty or failed listings are not cached, and expiration eventually allows new storage entries to appear.
