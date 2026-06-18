## sources/sync-backup/kopia/internal/cache/mutex_map_test.go

Purpose: unit tests for keyed mutex reference tracking and lock compatibility.

Important APIs/types/functions: `TestMutexMap_ExclusiveLock` and `TestMutexMap_SharedLock`.

Control flow, state, and persistence: tests acquire exclusive and shared locks, attempt incompatible try-locks, release locks, and assert entry-map sizes shrink as ref counts reach zero.

Dependencies and integration points: package-internal tests directly inspect `mutexMap.entries`.

Risks and test signals: confirms basic lock semantics and cleanup. Does not test high-concurrency races or misuse unlock paths.
