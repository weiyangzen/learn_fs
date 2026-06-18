# sources/storage-engines/pebble/objstorage/objstorageprovider/sharedcache/shared_cache_test.go

Purpose: This file tests shared-cache read behavior using data-driven fixtures and randomized concurrent reads.

Important tests and helpers: `TestSharedCache` walks `testdata/cache`, opens an object storage provider over a logging memory FS, initializes a `sharedcache.Cache`, writes deterministic object data, and issues `read` or `read-for-compaction` commands. It validates returned bytes and reports miss-count deltas after `WaitForWritesToComplete`. `TestSharedCacheRandomized` chooses shard counts and block sizes, writes a random-size object, and performs repeated reads from random offsets, optionally concurrently. Helpers parse byte-size arguments with K/M/G suffixes.

Control flow and state: Data-driven tests explicitly wait for asynchronous cache writes so a subsequent read can observe a hit. Compaction reads use `ReadOnly` and should not populate the cache. Randomized tests cover different block sizes, sharding block sizes, cache sizes, and concurrent read schedules.

Dependencies and integration: Tests use a real `objstorageprovider.Provider` for local object data, then pass its readable into `Cache.ReadAt`. This exercises cache logic against `objstorage.Readable`/`remote.ObjectReader`-like APIs without real remote storage.

Risks and test signals: The tests catch incorrect data reconstruction for unaligned offsets, shard/block boundary reads, partial hits, EOF capping, and basic concurrency races. The randomized seed is printed for reproduction. They do not assert detailed metrics or persistence across cache reopen.
