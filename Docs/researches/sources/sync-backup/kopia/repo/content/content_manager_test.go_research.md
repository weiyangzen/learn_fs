# sources/sync-backup/kopia/repo/content/content_manager_test.go

Final split target: `Docs/researches/sources/sync-backup/kopia/repo/content/content_manager_test.go_research.md`.

Purpose: comprehensive behavioral suite for `WriteManager` and related content storage behavior across index formats v1 and v2.

Important fixtures: `contentManagerSuite` runs under `TestFormatV1` and `TestFormatV2`. Helpers build map/faulty/eventually-consistent blob stores, fake clocks, format providers, seeded content, hash expectations, and assertion helpers for content presence, deletion state, blob counts, retries, and cache contents.

Control-flow coverage: tests cover empty flushes, zero-length content, small pack packing, deduplication in pending and uncommitted states, internal pack flush on size, many writes with reopen, failed pack upload retry, concurrent managers, index compaction, delete/undelete/rewrite sequences, delete/recreate timestamp ordering, parallel writes, flush barriers, retry behavior under fault injection, disabled index flush counters, content iteration, unreferenced pack scanning, read/write aliasing, format compatibility, own-writes consistency, compression, cache key separation, prefetch hints, permissive cache loading, and legacy index poison tolerance.

State and persistence behavior: the suite asserts the intended transitions from session marker to pack blob to index blob, visibility boundaries between writers before refresh/reopen, monotonic timestamps for deletion and recreation under frozen time, and durability after flush and manager reopen.

Dependencies and integration: uses `blobtesting`, `faketime`, `fault`, `ownwrites`, cache storage, `indexblob`, `epoch`, compression providers, and repository format construction.

Risks and signal value: this is the primary regression net for lock ordering, failed writes, deleted-entry precedence, format compatibility, and cache correctness. Some loops are reduced under test-complexity settings, so very high-scale behavior is sampled rather than exhaustive.
