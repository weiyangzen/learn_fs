# sources/sync-backup/restic/internal/backend/cache/backend_test.go

Purpose: Tests the cache backend wrapper around an underlying backend.

Important APIs and helpers: `loadAndCompare`, `save`, `remove`, `randomData`, and `list` drive common operations. `loadCountingBackend` counts backend loads; `loadErrorBackend` injects load errors. Tests include `TestBackend`, `TestOutOfBoundsAccess`, `TestForget`, `TestErrorBackend`, `TestAutomaticCacheClear`, and `TestAutomaticCacheClearInvalidFilename`.

Control flow and state: Tests save data directly and through wrapped backends, observe whether cache files exist, remove backend entries, call `Stat`/`List`, and verify cache cleanup. Concurrent error tests run several goroutines against a backend that fails loads to ensure waiters do not hang and successful fallback states remain valid.

Dependencies and integration: Uses `mem.New`, `backend/test.LoadAll`, `TestNewCache`, `restic.Hash`, and randomized data.

Risks and test signals: The suite guards cache population, stale entry removal on stat/list, no duplicate full downloads for bad ranges, error propagation, and the one-shot `Forget` circuit breaker.
