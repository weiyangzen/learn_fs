## sources/sync-backup/kopia/internal/cache/content_cache_concurrency_test.go

Purpose: stress tests content cache locking and fetch coalescing.

Important APIs/types/functions: cache constructors for data/metadata modes, prefetch/concurrency tests, `concurrencyTester`.

Control flow, state, and persistence: tests use `FaultyStorage` delays/fault hooks to observe when underlying `GetBlob` runs, then run concurrent `GetContent`/`PrefetchBlob` calls. They assert same-content races fetch once, different content IDs or blobs can fetch in parallel, and prefetch blocks content reads until full-blob caching is complete.

Dependencies and integration points: exercises `ContentCache`, `mutexMap`, `FaultyStorage`, and map-backed cache storage.

Risks and test signals: strong concurrency signal for avoiding duplicate fetches and over-serialization. Some goroutines ignore returned errors, so failures can manifest through counters/fault hooks rather than direct assertions.
