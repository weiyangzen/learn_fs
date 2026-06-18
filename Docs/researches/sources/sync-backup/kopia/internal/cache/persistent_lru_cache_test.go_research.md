# sources/sync-backup/kopia/internal/cache/persistent_lru_cache_test.go

Purpose: validates persistent LRU cache correctness, fault tolerance, nil behavior, protection mismatch handling, and default construction against map-backed blob storage.

Important APIs/types/functions: `TestPersistentLRUCache`, `TestPersistentLRUCache_Invalid`, `TestPersistentLRUCache_GetDeletesInvalidBlob`, `TestPersistentLRUCache_PutIgnoresStorageFailure`, sweep tests, `faultyCache`, and helpers `verifyCached`, `verifyNotCached`, `verifyBlobExists`, `verifyBlobDoesNotExist`.

Control flow: tests create map/faulty storages, instantiate `NewPersistentCache`, write blobs through `Put`, read with `TestingGetFull`/`GetOrLoad`, inject storage faults, corrupt stored bytes, close/reopen caches, and assert storage-visible blob presence.

State and persistence behavior: tests prove entries persist across cache instances, protection keys gate readability, corrupted entries are treated as misses and scheduled for deletion, and sweep decisions are observable in the backing `DataMap`.

Dependencies/integration: uses `blobtesting`, `cacheprot.ChecksumProtection`, `clock.Now`, `fault`, `gather`, `testlogging`, `testutil`, and `blob` errors.

Risks/test signals: good coverage for single-thread behavior and storage errors, but little concurrency stress. Sleep-based sweep timing can be slow/flaky if timing thresholds change. The file documents that `Put` logs but does not propagate storage write failures.
