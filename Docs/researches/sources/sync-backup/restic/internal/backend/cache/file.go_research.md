# sources/sync-backup/restic/internal/backend/cache/file.go

Purpose: Implements per-file cache persistence, loading, saving, forgetting, clearing, listing, and existence checks.

Important APIs and methods: `Cache.filename`, `canBeCached`, `load`, `save`, `Forget`, `remove`, `Clear`, `list`, `Has`, and `isFile`. Cacheable types are defined in `cache.go`.

Control flow and state: Cached filenames are sharded by the first two handle-name characters under type-specific directories. `load` opens a cache file, validates requested range, seeks, and optionally limits the reader. `save` creates the shard directory, writes to a temp file, closes it, then atomically renames into place; Windows permission errors during rename-over-open are treated as success. `Forget` normalizes metadata handles, removes at most once per process via `forgotten`, and prevents repeated delete/re-cache loops. `Clear` removes cache files not present in a valid ID set. `list` walks cache subdirectories and returns file basenames.

Persistence and dependencies: Persists cached files on local disk and uses temp files plus rename for concurrent-process safety. Depends on `backend`, `util.LimitReadCloser`, `os`, `filepath`, `runtime`, and `pkg/errors`.

Integration points: Used by `cacheBackend` for transparent loading/saving and pruning. It assumes valid restic IDs are long enough for two-character sharding.

Risks and test signals: Risks include panics for too-short names, stale or corrupt cached files, range validation mismatches, concurrent save/load behavior, Windows rename semantics, and damaged cache directories. `file_test.go` covers file operations, range loads, concurrent saves, and damaged-cache save failure.
